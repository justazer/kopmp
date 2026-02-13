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
Get Sales Invoices related to loans and savings.

- **Endpoint**: `kopmp.utils.invoice.get_loan_invoices`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `flow_type` (str, optional): 'income' or 'outcome'

---

## 6. Simpanan (Saving)

### Get Simpanan Pokok List
Get all Simpanan Pokok members.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_pokok.simpanan_pokok.get_list`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)

### Get Simpanan Pokok Detail
Get Simpanan Pokok detail by User Profile ID.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_pokok.simpanan_pokok.get_detail`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `profile_id` (str): User Profile ID

### Get Simpanan Pokok Detail By ID
Get Simpanan Pokok detail by its ID.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_pokok.simpanan_pokok.get_detail_by_id`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `simpanan_pokok_id` (str): Simpanan Pokok ID

### Get Simpanan Wajib List
Get all Simpanan Wajib members.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_wajib.simpanan_wajib.get_list`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)

### Get Simpanan Wajib Detail
Get Simpanan Wajib detail by User Profile ID (includes logs).

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_wajib.simpanan_wajib.get_detail`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `profile_id` (str): User Profile ID

### Get Simpanan Wajib Detail By ID
Get Simpanan Wajib detail by its ID (includes logs).

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_wajib.simpanan_wajib.get_detail_by_id`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `simpanan_wajib_id` (str): Simpanan Wajib ID

### Get Tagihan List
Get list of all Simpanan Tagihan (Pokok + Wajib).

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_pokok_tagihan.simpanan_pokok_tagihan.get_tagihan_list`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `profile_id` (str, optional): Filter by User Profile ID

### Pay Simpanan Pokok Tagihan
Pay a Simpanan Pokok Tagihan.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_pokok_tagihan.simpanan_pokok_tagihan.pay_simpanan_pokok_tagihan`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `tagihan_id` (str): Tagihan ID

### Pay Simpanan Wajib Tagihan
Pay a Simpanan Wajib Tagihan.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_wajib_tagihan.simpanan_wajib_tagihan.pay_simpanan_wajib_tagihan`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `tagihan_id` (str): Tagihan ID

---

## 7. Simpanan Pencairan (Withdrawal)

### Get Simpanan Pencairan List
Get all Simpanan Pencairan requests.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_pencairan.simpanan_pencairan.get_list`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)

### Get Simpanan Pencairan Detail
Get Simpanan Pencairan requests for a specific user profile.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_pencairan.simpanan_pencairan.get_detail`
- **Method**: `GET`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `profile_id` (str): User Profile ID

### Approve/Reject Simpanan Pencairan
Approve or reject a withdrawal request.

- **Endpoint**: `kopmp.kopmp.doctype.simpanan_pencairan.simpanan_pencairan.approve_pencairan`
- **Method**: `POST`
- **Access**: Public (Guest Allowed)
- **Parameters**:
  - `pencairan_id` (str): Pencairan ID
  - `action` (str): 'approve' or 'reject'
