# Integrasi ERPNext dengan App Kopmp

Dokumen ini menjelaskan teknis integrasi antara aplikasi `kopmp` (Manajemen Koperasi) dengan modul standar ERPNext, khususnya modul Accounting dan Selling.

## 1. Arsitektur Integrasi

Integrasi dilakukan melalui beberapa mekanisme:
1.  **Hooks & Event Listeners**: Mendengarkan perubahan status pada dokumen ERPNext (misal: Payment Entry).
2.  **Custom Fields (Fixtures)**: Menambahkan field khusus pada dokumen standar ERPNext (misal: Sales Invoice) untuk menyimpan referensi ID Pinjaman.
3.  **Direct API Calls**: Fungsi Python di `kopmp` yang memanggil API standar ERPNext `frappe.new_doc()` untuk membuat Invoice dan Customer.

## 2. Poin Integrasi Database (DocType)

### Sales Invoice (Faktur Penjualan)
App ini menambahkan field custom (`custom_*`) ke Sales Invoice untuk menghubungkan tagihan dengan data pinjaman:

| Field Name | Deskripsi |
|------------|-----------|
| `custom_pinjaman_id` | Link ke dokumen `Pinjaman` |
| `custom_pinjaman_pencairan_id` | Link ke dokumen `Pinjaman Pencairan` (jika invoice pencairan) |
| `custom_pinjaman_installment_id` | Link ke dokumen `Pinjaman Installment` (jika invoice angsuran) |
| `custom_invoice_type` | Menandai tipe invoice: `Disbursement` atau `Installment` |
| `custom_installment_number` | Nomor angsuran (ke-n) |

Field ini didefinisikan dalam `hooks.py` di bagian `fixtures` dan diexport sebagai Custom Field.

### Customer (Pelanggan)
Setiap peminjam (UserProfile) di `kopmp` akan dibuatkan data **Customer** di ERPNext.
- **Naming Series**: `CUST-{profile_id}`
- **Customer Group**: `Loan Borrowers` (Dibuat otomatis)

## 3. Alur Proses Bisnis

### A. Pencairan Pinjaman (Loan Disbursement)
*File logic: `kopmp/utils/invoice.py` -> `create_disbursement_invoice`*

Saat `Pinjaman Pencairan` disetujui:
1.  Sistem membuat **Sales Invoice** baru.
2.  **Customer** diambil dari Profile peminjam.
3.  **Item Lines**:
    - `LOAN-DISB`: Sebesar nominal pencairan (Income Account: *Loans Receivable/Piutang Pinjaman*).
    - `LOAN-ADMIN-FEE`: Biaya admin (Income Account: *Loan Income/Pendapatan Pinjaman*).
4.  Invoice disimpan dalam status Draft (atau Submit tergantung konfigurasi).

### B. Tagihan Angsuran (Installment Invoice)
*File logic: `kopmp/utils/invoice.py` -> `create_installment_invoices`*

Semua angsuran (`Pinjaman Installment`) akan digenerate menjadi **Sales Invoice**:
1.  **Item Lines**:
    - `LOAN-INST-PRINCIPAL`: Pokok angsuran.
    - `LOAN-INST-INTEREST`: Bunga angsuran.
2.  Sales Invoice direferensikan kembali ke dokumen `Pinjaman Installment` pada field `installment_invoice`.

### C. Pembayaran (Payment Entry)
*File logic: `kopmp/utils/payment.py`* & *Hooks*

Integrasi dua arah terjadi saat User melakukan pembayaran via ERPNext (Payment Entry):
1.  **Hook `on_submit`**: Trigger fungsi `update_installment_payment_status`.
2.  Sistem mengecek apakah Payment Entry mereferensikan Sales Invoice yang memiliki `custom_pinjaman_installment_id`.
3.  Jika ya, sistem mengupdate status `Pinjaman Installment`:
    - Update `paid_amount`, `paid_date`.
    - Update status menjadi `Paid`, `Partial`, atau `Unpaid`.
4.  **Hook `on_cancel`**: Jika Payment Entry dibatalkan, status di Installment akan dikembalikan (reverted).

## 4. Master Data Otomatis

File `kopmp/setup_loan_integration.py` memastikan ketersediaan data master di ERPNext:

### Item (Layanan)
- `LOAN-DISB` (Loan Disbursement)
- `LOAN-ADMIN-FEE` (Loan Administration Fee)
- `LOAN-INST-PRINCIPAL` (Loan Installment - Principal)
- `LOAN-INST-INTEREST` (Loan Installment - Interest)

### Akun (Chart of Accounts)
Script akan mencoba membuat akun jika belum ada:
- **Loans Receivable** (Asset): Untuk menampung piutang pinjaman.
- **Loan Income** (Income): Untuk menampung pendapatan bunga dan admin.

## 5. Ringkasan File Penting

- **`kopmp/hooks.py`**: Pendaftaran event listener `Payment Entry` dan custom fields.
- **`kopmp/utils/invoice.py`**: Logika pembuatan Sales Invoice.
- **`kopmp/utils/payment.py`**: Logika update status pembayaran dari ERPNext ke Kopmp.
- **`kopmp/utils/customer.py`**: Sinkronisasi Profil User ke Customer ERPNext.
- **`kopmp/setup_loan_integration.py`**: Setup awal master data (Items, Accounts).
