# Action Endpoint Manager (`action_endpoint`)

The **Action Endpoint Manager** is a lightweight, high-performance module designed for **Odoo 19**. It automates the packaging and conversion of backend model methods into isolated, secure **API Endpoints (Server Actions)**. 

Built on the **KISS (Keep It Simple, Stupid)** philosophy and a **Fail-Safe** architectural design, this module completely eliminates complex signature mapping at the integration layer. It forces all endpoints to execute seamlessly at the Model level (`@api.model`) and leverages `self.env.context` as a secure black box for data transfer.

---

## 🚀 Key Features

* **Zero-Configuration `@endpoint` Decorator:** Automatically registers metadata and wraps the method with Odoo's native `@api.model`. No technical parameters required from the developer.
* **Centralized Integration Hub:** A clean Odoo 19 interface utilizing the modern `<list>` view architecture. Manage, monitor, and synchronize all endpoints for any model in one place.
* **Native Payload & Return Mapping:** Automatically generates Server Actions with the execution pattern `action = model.method_name()`. This allows python methods to return responses (Dict, List, String) directly back to HTTP/JSON Controllers.
* **Encapsulated Security:** Endpoints are strictly forced to be hidden from the UI's "Action" drop-down menu, keeping them clean for headless API usage. Dependencies are safely handled via `ondelete='cascade'`.

---

## 🛠️ Developer Usage Guide

Building and consuming an API endpoint is streamlined into three simple steps:

### Step 1: Decorate the Method in Your Model
Define a clean, parameterless model method. Extract incoming request data directly from `self.env.context` and return the response payload.

```python
# file: custom_module/models/hr_contract.py
from odoo import models
from odoo.addons.action_endpoint.decorators import endpoint

class HRContract(models.Model):
    _name = 'hr.contract'
    _description = 'HR Contract'

    @endpoint(name="API Reject Contract")
    def api_reject_contract(self):
        # 1. Extract implicit data sent from the Controller via context
        contract_number = self.env.context.get('contract_num')
        reason = self.env.context.get('reject_reason', 'No reason provided')
        
        # 2. Execute core business logic
        contract = self.search([('number', '=', contract_number)], limit=1)
        if not contract:
            return {'status': 'error', 'message': 'Contract not found'}
            
        contract.write({
            'state': 'rejected',
            'notes': reason
        })
        
        # 3. Return payload directly back to the Server Action runner
        return {
            'status': 'success', 
            'contract_id': contract.id
        }
```

---

## Step 2: Generate the Endpoint via UI

Navigate to: **Settings → Technical → Action Endpoints → Quản lý Endpoints**

1. Click **New**, đặt tên cấu hình và chọn model đích (e.g., `hr.contract`)
2. Click button **"Sinh Endpoint Actions"** trên header
3. Hệ thống sẽ tự động:
   - Scan model
   - Generate execution string (e.g., `action = model.api_reject_contract()`)
   - Liệt kê trong notebook
   - Refresh view


## Step 3: Trigger the Endpoint from an HTTP/JSON Controller

Inject payload từ request vào context bằng `.with_context()` rồi execute Server Action qua `.run()`.

```python
# file: custom_module/controllers/main.py
from odoo import http
from odoo.http import request


class ContractApiController(http.Controller):

    @http.route('/api/contract/reject', type='json', auth='public', methods=['POST'])
    def reject_contract_api(self):

        # Retrieve the JSON payload submitted by the external client
        payload = request.get_json_data()
        # Expected: {'contract_num': 'HD-2026', 'reject_reason': 'Invalid salary'}

        # Browse the auto-generated Server Action (e.g., ID 93)
        action_server = request.env['ir.actions.server'].sudo().browse(93)

        # Execute the action. .run() returns model result
        response_data = action_server.with_context(**payload).run()

        return response_data
```

---

## ⚠️ Important Considerations

### 🔐 Access Control & Security

Khi expose endpoint với `auth='public'`, luôn execute server action với elevated privileges:

```python
.sudo()
```

Nếu không, sẽ phát sinh `AccessError` do ACL restrictions.