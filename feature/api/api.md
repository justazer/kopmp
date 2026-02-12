# Koperasi App API Documentation

This document outlines the available APIs for the Koperasi App (kopmp). All APIs respond with a standard JSON structure.

## Base URL
`/api/method/`

## Authentication
APIs with `allow_guest=True` can be accessed without authentication. For others, use standard Frappe authentication (token/password).

---

## 1. Pinjaman (Loan Application)

### Create Pinjaman
Create a new loan application.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman.pinjaman.create_pinjaman`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `profile_id` (str): User Profile ID
  - `pinjaman_produk_id` (str): Pinjaman Produk ID
  - `nominal` (float): Loan Amount
  - `top` (str): Term of Payment (Tenor)
  - `rate` (float): Interest Rate
  - `start_date` (str): Start Date (YYYY-MM-DD)
  - `end_date` (str): End Date (YYYY-MM-DD)

- **Response**:
```json
{
  "message": "success",
  "data": { ...Pinjaman Document... }
}
```

### Get Pinjaman List
Get all Pinjaman applications, optionally filtered by User Profile.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman.pinjaman.get_pinjaman`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `profile_id` (str, optional): User Profile ID

- **Response**:
```json
{
  "message": "success",
  "data": [ ...List of Pinjaman Dicts... ]
}
```

### Process Pinjaman (Approve/Reject)
Approve or Reject a Pinjaman application.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman.pinjaman.process_pinjaman`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `pinjaman_id` (str): Pinjaman ID
  - `action` (str): 'approved' or 'reject'

- **Response**:
```json
{
  "message": "success",
  "data": { ...Updated Pinjaman Document... }
}
```

### Get Contracts with Outstanding Installments
Get approved loans that have outstanding installments.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman.pinjaman.get_list_kontrak_pinjaman`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `profile_id` (str, optional): User Profile ID

- **Response**:
```json
{
  "message": "success",
  "data": [ ...List of Pinjaman Dicts... ]
}
```

---

## 2. Pinjaman Installment

### Get Installments
Get all installments for a specific loan.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_installment.pinjaman_installment.get_installments`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `pinjaman_id` (str): Pinjaman ID

- **Response**:
```json
{
  "message": "success",
  "data": [ ...List of Installment Dicts... ]
}
```

### Pay Installment (Wrapper)
Mark an installment as paid using a simple wrapper function.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_installment.pinjaman_installment.pay_installment`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `installment_id` (str): Pinjaman Installment ID

- **Response**:
```json
{
  "message": "success",
  "data": { ...Updated Installment Document... }
}
```

---

## 3. Pinjaman Pencairan (Disbursement)

### Get Pencairan List
Get disbursement data.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_pencairan.pinjaman_pencairan.get_pencairan_by_pinjaman`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `pinjaman_id` (str, optional): Filter by Pinjaman ID

- **Response**:
```json
{
  "message": "success", // or "not found"
  "data": [ ...List of Pencairan Dicts... ]
}
```

### Process Pencairan (Approve/Reject)
Approve or Reject a disbursement request.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_pencairan.pinjaman_pencairan.process_pencairan`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `pencairan_id` (str): Pencairan ID
  - `action` (str): 'approved' or 'reject'

- **Response**:
```json
{
  "message": "success",
  "data": { ...Updated Pencairan Document... }
}
```

---

## 4. Pinjaman Produk (Product Management)

### Get All Products
Fetch all loan products.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_produk.pinjaman_produk.get_all_pinjaman_produk`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)

### Get Product TOPs
Fetch tenors for a specific product.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_produk.pinjaman_produk.get_pinjaman_produk_top`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `pinjaman_produk_id` (str): Product ID

### Create Product
Create a new loan product.

- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_produk.pinjaman_produk.create_pinjaman_produk`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**: `tipe`, `admin_fee`, `start_date`, `end_date`, `status`

### Update Product
- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_produk.pinjaman_produk.update_pinjaman_produk`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**: `pinjaman_produk_id` + fields to update

### Toggle Product Status
- **Endpoint**: `kopmp.kopmp.doctype.pinjaman_produk.pinjaman_produk.toggle_status_pinjaman_produk`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**: `pinjaman_produk_id`

### Create/Update TOP
- **Create**: `kopmp.kopmp.doctype.pinjaman_produk.pinjaman_produk.create_pinjaman_produk_top`
- **Update**: `kopmp.kopmp.doctype.pinjaman_produk.pinjaman_produk.update_pinjaman_produk_top`

---

## 5. Invoices

### Get Loan Invoices
Get Sales Invoices related to loans.

- **Endpoint**: `kopmp.utils.invoice.get_loan_invoices`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `flow_type` (str, optional): 'Disbursement' or 'Installment'
