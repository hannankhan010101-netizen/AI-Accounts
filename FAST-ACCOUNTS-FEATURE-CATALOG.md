# Fast Accounts — End-to-End Feature & Flow Catalog

This document lists **product features and user-visible flows** from **public Fast Accounts materials** and from **in-app structure** shared for this project (sidebar screenshots, Reports / Analytical Reports screens, and dashboard layout descriptions). It is written as a **functional blueprint** for building a like-for-like application.

**Verification note:** **Operator / master** areas (for example `…/administrator/…`) and any menus not yet captured here still need a dedicated inventory. **Dashboard numbers, customer/supplier names, and balances** are omitted from this file on purpose (structure only); use your live system for real data. For **where each major UI is documented**, use **§16.1**; for **public source URLs** and **screenshot / sensitive-data policy**, use **§16**; for **what is still uncaptured**, use **§15**.

**Sources:** support center, feature and pricing pages, product announcements, digital invoicing and roles documentation, developer API onboarding, and **live UI excerpts** aligned to `my.fastaccounts.io`.

**Where the deep live UI lives:** **Navigation and chrome** (**§2** — sidebar **§2.1**, support/marketing taxonomy **§2.2**, global header **§2.3**, assembly entry note **§2.4**, general journal entry **§2.5** → **§9.2.1**, official tutorial map **§2.6**); **Cross-cutting capabilities** (**§3** — documents, print, import, tax/FX, audit, etc.); **Operational modules** (feature flows **§4**–**§8** including **§8** fixed assets; assembly **§11**); **General ledger and COA** (**§9** — chart/nominals/sections **§9.1**, journals **§9.2**, budget **§9.3**, taxes/year-end pointer **§9.4** / **§12.12**, lock date **§9.5**); **reporting hubs** (**§10** — especially **§10.3**, **§10.9**–**§10.12**); **company Settings** (**§12** — mega-menu **§12.1**, Smart Settings, users/roles, taxes, business info, content settings, user log). **Narrative journeys** **§13**; **abbreviations** **§14**; **uncaptured parity** **§15**. **§16** — **route ↔ section** index (**§16.1**) plus **public URLs** and **in-app screenshot** policy for maintainers.

---

## 1. Product entry, identity, and tenancy

### 1.1 Access and onboarding

- **Sign up** for a new company account (marketing / portal links from the public site).
- **Login** to the cloud application (`my.fastaccounts.io`).
- **Forgot password** self-service.
- **Google Sign-In** (social login) as an alternative to password login.
- **Two-factor authentication (2FA)** for stronger account protection.
- **Getting started / quick tour** content (tutorials and setup guides on the marketing site).

### 1.2 User types (within a company)

- **Admin user:** full access to the system, including adding and managing other users.
- **Standard user:** access limited to modules and actions granted by assigned **roles** and optional **fixed** field locks (detailed under **User management** in the Settings section).

### 1.3 Subscription and capacity

- **User limits** tied to subscription package; additional users may require contacting support (as described in roles documentation).

### 1.4 External connectivity (product capability)

- **Developer / API access** can be enabled for an account (often via account manager in published API onboarding).
- **API users** are a distinct user type: created under user management, assigned a role, then issued **API key / secret** after **email OTP** confirmation.
- **IP restriction** at user level (optional) for tighter access control (also reflected in API error handling for invalid IP in public API docs).

### 1.5 Commercial, onboarding, and learning surfaces (product-facing)

These are part of how Fast Accounts is **sold and delivered**, not only accounting screens:

- **Packages** (public pricing pages describe tiers such as **Basic**, **Standard**, **Plus+**, and **Premium**) with differing included modules and **user seat counts** (published examples include **1 / 3 / 5 / 10** users depending on tier).
- **Optional add-ons** (priced separately on public pages), including at least: **Batch & Expiry**, **Letter of Credit**, **Advanced user rights**, **Analytical reports**, **Emails**, **API keys**, **Online payments**, **Budget**, **Authorisation**, **Fixed asset** module.
- **Free trial** with access comparable to a **Standard**-style experience during working hours support (per public FAQ wording).
- **Data migration** from other accounting products marketed as a supported onboarding path.
- **Subscription billing** flexibility: monthly vs annual presentation on public pages; payment methods for subscriptions described in FAQs include **cash, card, bank transfer, cheque** (commercial billing, not bank module payment modes).
- **Free training upon setup** and ongoing **support** positioning; **24/7 support** claim in public FAQ text.
- **Paid advanced training:** an **8-week Certification Course in Digital Accounting** (partner-delivered, paid).
- **Getting-up-to-speed** style onboarding education for new subscribers (FAQ).
- Public **FAQs**, **policies** (privacy, refund/cancellation, payment, terms), **contact**, **tutorials**, **case studies**, **blog**, **developers** portal entry — navigation and trust content wrapped around the app.
- **Partner with us** / commercial partner narratives appear on the public site (channel program; not core ledger features).
- Public FAQ text at times references **three** packages while pricing pages show **four named tiers**; treat **package names, limits, and included modules** as **version-dependent** and re-verify against the live pricing screen when cloning commercially.

---

## 2. Global navigation model (main menu)

### 2.1 In-application main sidebar (live layout)

Verified from **logged-in company UI** (collapsible groups, chevron expand/collapse):

| Top-level | Sub-items (as shown) |
|-----------|----------------------|
| **Dashboard** | *(home — summary widgets; see §10.9)* |
| **Bank** | **Account Balances**, **Bank Payments**, **Bank Receipts**, **Transfers**, **Reconciliation**, **Import Statement** |
| **Sales** | **Invoices**, **Receipts**, **Post Dated Cheque Received**, **Sales All**, **Orders**, **Customers** |
| **Purchases** | **Bills**, **Payments**, **Post Dated Cheque Issued**, **Purchases All**, **PO**, **Suppliers** |
| **Inventory** | **Products**, **Stock Adjustment** *(additional inventory tools from documentation—e.g. stock transfer, landed cost, LC, batch/expiry—may appear in the same group or via settings when the module is licensed)* |
| **Reports** | Top-level entry to the **Reports** hub (see §10.10) |
| **Analytical Reports** | Separate top-level entry to the **Analytical Reports** hub (see §10.3) |

**Post-dated cheques:** distinct sub-areas for **received** (sales side) vs **issued** (purchases side) support PDC workflows alongside normal receipts/payments.

**“Sales All” / “Purchases All”:** aggregate entry points for cross-type purchase/sales work (exact scope = unified search/list vs multi-doc-type launcher; confirm in live app).

**Bank → Import Statement:** bank **statement file** import path (alongside reconciliation), distinct from **Excel voucher import** for bank payments/receipts described in announcements.

**Sidebar vs public help menus:** official support navigation sometimes lists **Bank → Revaluation** and **Bank → Multi Currency** as separate items. Those capabilities are still documented in **§4.6**–**§4.7** and **§3.13**; they may appear as **settings**, **wizards**, or **non-sidebar** actions in your build—confirm where **FX revaluation** lives for your tenant.

**Quotations:** public docs place **Quotations** under Sales; they may be reached via **Orders**, **Sales All**, or a **+ New** menu rather than a dedicated permanent sidebar row—confirm in your UI.

### 2.2 Support-site and marketing taxonomy (reference)

Public materials also describe these **primary areas** and modules: **Assembly**, deep **Settings**, **Letter of credit**, **Landed cost**, **Batch & expiry**, **Multi-location**, **Projects**, **Budget**, **Fixed assets**, **Authorisation**, **Emails**, **APIs**, **Online payments**, etc. Some appear under **Settings** or **Reports** in-app rather than as permanent sidebar roots for every company.

**Additional named product modules** on pricing/marketing (may be add-ons or tier-gated):

- **Projects**, **Multi-unit**, **Multi-currency**, **Multi-location**, **Landed costs**, **Attachments**
- **Fixed assets**, **Emails**, **Online payments**, **API keys**, **Budget**, **Authorisation**

Within each area, users work through **list screens → action menus → add/edit/detail → print / import / export / copy** patterns repeatedly.

The public **support** site classifies help articles under **Accounting**, **Business**, **Team**, and **Tech** (knowledge-base browsing; not identical to in-app menu names).

### 2.3 Global chrome (live header + settings rail)

**Top bar** (behind overlays): product branding, **current company** dropdown (switch context), **My Tasks**, **clock / activity** icon, **Support**, **user profile** entry that can open the **Settings** mega-menu.

**Settings overlay** (see **§12.1**): opens as a **large modal** with multi-column links and a **right rail** for **Switch company**, **Profile**, **Change password**, **Dark mode**, and **Logout**; modal **close** control (e.g. top-right **X**).

**Still verify per tenant:** notifications bell, environment banner, footer links, and any **admin-only** chrome not shown in captures.

### 2.4 Assembly operational entry (clarification)

**Assembly** appears as a **Reports** category (see §10.10) and as a full **Assembly module** in documentation (§11). Operational **jobs/templates** screens may be under **Inventory**, **Settings**, or a **Manufacturing** entry not visible in the narrow sidebar captures—map this when you record the full menu tree.

### 2.5 General journal entry point

**Journals** (manual GL / journal entry) appear under the **Settings** mega-menu: **Journals** link in the first column (§12.1), opening the **Journals** list (**§9.2.1**). They are also referenced from transactional **Print journal** flows (§3.7).

### 2.6 Official tutorial sidebar map (support site — full trail)

The [getting started / tutorial navigation](https://fastaccounts.io/getting-started-with-fast-accounts/) lists a **complete** module trail used in help content. **Compare** to §2.1: items here may be **licensed**, **regional**, or **moved** in your tenant’s live sidebar.

| Area | Topics linked in official sidebar |
|------|-----------------------------------|
| **Bank** | Account Balances; Bank Payments; Bank Receipts; Transfers; **Reconcile**; **Revaluation**; **Multi Currency** |
| **Sales** | Invoices; Receipts; Orders; Customers *(plus live-only: Post Dated Cheque Received; Sales All — §2.1)* |
| **Purchases** | Bills; Payments; Purchase Orders; Suppliers *(plus live-only: Post Dated Cheque Issued; Purchases All — §2.1)* |
| **Inventory** | Products; **Stock Transfer**; Stock Adjustment; **Landed Cost**; **Letter of Credit**; **Projects**; **Multi Unit**; **Batch and Expiry** *(live capture showed only Products + Stock Adjustment — §2.1)* |
| **Reports** | Reports; Analytical Reports |
| **Assembly** | Assembly; **Jobs**; **Templates** |
| **Settings** | Settings; Advance Users; Authorisation; Budget; Location; Printing; Taxes; Journal; User Roles and Rights; Lock Date; Nominal Codes |
| **Others** | General; Attachments |

**Support hub filters** (browsing help articles): **All**, **Bank**, **Sales**, **Purchases**, **Inventory**, **Reports**, **Assembly**, **Settings**, **Others** — plus content tags **Accounting**, **Business**, **Team**, **Tech** on the support site.

---

## 3. Cross-cutting capabilities (apply across modules)

### 3.1 Smart Settings (central configuration)

- The live **Smart Settings** screen is documented section-by-section in **§12.2** (accordion list, **Others** toggles, **Sales/Purchases/Bank/Fixed assets** smart filter & doc labels, **E-signatures**, **product description** grid, **template/draft** matrix, **last rate** matrix, **auto codes**, **currency & time zone**). **Tax rates**, **tax regions**, **year end**, and **supplier/customer tax display** matrix live on **Taxes and Year End** (**§12.12**), not inside this accordion. **Company name, address, logo, contact, and registration IDs** for prints live on **Business Information** (**§12.13**). **List column** layout (Forms / Menu / Listing) is **Content Settings** (**§12.14**). **User / audit log** inquiry is **§12.15**. **Chart of Account**, **nominal**, and **section** maintenance are **§9.1** (not Smart Settings).
- **Smart filter** and **smart doc** labels configured here drive the **Filter1–4** and **SmartDocNo1–4** behavior on documents (see also §3.2).
- **Auto code** generation UI: **customer**, **supplier**, **product**, **location**, **project**, **WHT**, **GST**, **ADT**, **FED**, **nominal** (§12.2.8)—overlaps with announcements that listed overlapping entity types.

### 3.2 Documents, numbers, and references

- **Automatic voucher numbers** on listings (for example **“V. No.”** columns) for bank payments, bank receipts, bank transfers, sales receipts, and supplier payment screens.
- **Journal numbers** on journal listings when posting journals.
- **Document references** and **multiple “smart” document number** slots on sales documents (public API describes multiple smart doc number fields).
- **Filters** on sales documents (multiple filter fields; system may auto-create filter values when new ones appear on transactions).

### 3.3 Templates and recurrence

- **Transaction templates:** save a transaction layout/details for reuse.
- **Recurring transactions:** schedule automatic creation on defined dates.

### 3.4 Draft, approval, and audit

- **Draft transactions** that do not affect financials until approved.
- **Approval workflow:** one user records, another approves before financial effect.
- **User log:** records add / modify / delete activity for accountability; the live **User Log** inquiry screen opens from the **Settings** mega-menu → **Log Management** (listed under the **Journals** column in live UI — **§12.15**).

### 3.5 Attachments

Attachments can be stored against (per announcement):

- Bank payments, bank receipts, bank transfers  
- Sales invoices, sales orders  
- Customer receipts  
- Supplier bills, purchase orders, supplier payments  
- Journals (general journal area)

### 3.6 Communications

- **Email sales invoices** directly to customers from the application.
- **SMS module:** configurable SMS messages triggered around events such as **sales invoice**, **customer balance reminder**, **supplier payment**, subject to SMS credits/settings where applicable.

### 3.7 Printing

- **Print templates** for sales and purchases, including multiple customizable layouts for:
  - **Sales Invoice (SI)**
  - **Sales Credit (SC)** *(live Settings menu uses **SC** for sales credit printing)*  
  - **Sales Order (SO)**
  - **Sales Receipt (SR)**
  - **Post-dated cheque received (PDCR)** — Settings → Sales Printing (live UI; §14)
  - **Delivery Note from Sales Invoice (GDNSI)**
  - **Delivery Note from Sales Order (GDNSO)**
  - **Customer (CUS)** print target (live Settings — §12.1)
  - **Purchases side:** **VI**, **VC**, **PO**, **VP** (bill payment), **PDCI**, **GRNPO**, **GRNVI** (live Settings — §12.1; codes summarized in §14)
  - Older announcements sometimes list only a subset; **Settings mega-menu** is the full print-matrix source in live product.
- **Journal printing** available from transactional screens across **Sales (invoices, receipts)**, **Purchases (bills, payments)**, **Bank (payments, receipts, transfers)**, and **General Journal**, with **customizable journal print layouts**.
- **Bank voucher printing** vs **journal printing** choice on bank screens (voucher-style vs traditional debit/credit journal presentation).
- **Two copies** printing option for **sales receipts** and **bill payments** (side-by-side duplicate on one page), controlled from **Sales Receipts** settings.

### 3.8 Import and export

- **Excel import** for **bank payments and receipts** (multi-line vouchers; **group number** column to split one file into multiple voucher IDs).
- **Excel import** for **journal** and **bank** data with evolving templates (for example **project name** column added in a template update).
- **Bulk import of product opening stock** after products exist.
- **Product bulk actions** screen: bulk update of **taxes** and other product data by category/product selection.
- Reports: **export to Excel** (transaction type column appears on exports per general article).

### 3.9 Copy and batch entry

- **Copy** existing **sales invoices**, **journals**, and **bank payments** into new entries (action menu opens a pre-filled new document).
- **Batch sales invoice** entry screen (multi-line / multi-item workflow).
- **Batch supplier bills** screen.

### 3.10 List usability and analysis

- **Hyperlinks inside reports** to drill from a report line into underlying transaction/account detail.
- **Column management / global customization** of fields and columns on lists (organization-wide list layout management). **Content Settings** (**§12.14**) is the live **Forms / Menu / Listing** hub for **reorder, rename, and show/hide** on specific grids; the Settings mega-menu also lists **Column Management** separately—map any overlap when you inventory that screen.
- **Customer listing: actions and filter tabs** (dedicated article; implies rich list filtering and row actions beyond simple search).

### 3.11 Multi-dimensional tagging

- **Projects:** optional **project codes** on transactional lines (sales, purchases, bank) when project accounting is enabled.
- **Locations / multi-location inventory:** optional **location codes** on documents when multi-location is enabled; stock by location.

### 3.12 Tax and pricing mechanics (cross-module)

- **GST / VAT** with product- and location-varying rates; **withholding tax** handling on receipts and payments.
- **Additional taxes** (for example **non-filer additional tax**, **Federal Excise** style charges): up to **two additional tax charges** on **sale invoices/credits/orders** and **supplier bills/credits/purchase orders** (per announcement).
- **Sales tax amount override** (authorized users) when automatic calculation is insufficient.
- **Filer vs non-filer** tax code patterns on products (public API shows separate tax code fields for non-filer customers).
- **Schedule 3 vs non–Schedule 3** distribution tax handling (distribution vs inline **invoice templates**).
- **Withholding income tax** on **customer receipts** and **supplier payments** (including advance-payment scenarios).
- **Central configuration** of **year end**, **which taxes appear** for supplier vs customer, **regional rate tables**, and **withholding rate rows** is on **Settings → Taxes and Year End** (§12.12)—a **separate** page from **Smart Settings** (which holds **WHT/GST/ADT/FED** *auto code* numbering—§12.2.8).

### 3.13 Currency

- **Multi-currency** operation: foreign currency on customers, banks, and documents with **exchange rates**.
- **Realized** and **unrealized** foreign exchange **gains/losses** handling (public multi-currency module description); **bank revaluation** supports closing-style FX treatment on foreign bank balances.

### 3.14 Period control

- **Lock date** to prevent edits/deletes before a chosen date (admin-controlled).
- **Per-user lock date** extension (stricter control: different users may have different effective lock dates).

### 3.15 Inventory costing support (where applicable)

- **FIFO allocation** option when applying **customer receipts** and **supplier payments** against outstanding invoices/bills (auto-suggestion behavior).

### 3.16 Distribution and wholesale pricing patterns

Per **distribution business** positioning:

- Line economics can include **discount**, **retail margin**, and **trade offer** (including per-product and customer-level combinations).
- **Sale rate factor (%)** for **fixed list price** businesses (rate adjustment layer on invoices).

### 3.17 Dimensional selling

- **Width × length → area** quantity calculation for **sales invoices** and **supplier bills** (flooring-style selling).

### 3.18 Digital compliance (jurisdiction-specific)

- **Digital invoicing** integration aligned with **FBR** requirements (Pakistan), including **test digital invoices**, **account setup for digital invoicing**, and **PRAL** integration overview materials.
- Regulatory notices linked from marketing pages (for example corporate mandate timelines).

### 3.19 Emails module (optional add-on)

- Distinct from ad hoc **email this invoice**: a module for **automated email triggers** and **personalized templates** to keep **customers and suppliers** informed about **balances**, **receipts**, and **payments** (public module marketing).

### 3.20 Online payments (optional add-on)

- **Integrated online payment / recovery** flows with third-party gateways publicly named as **PayPro** and **Kuickpay**, reducing manual re-keying of received payments (public pricing/module description).

### 3.21 Broader integrations (marketing level)

- Positioning: integrate with **other business systems**, **e-commerce / website** order flows, and **revenue/tax authority** services for **live reporting** of sales data where applicable (general marketing; jurisdiction-specific programs such as FBR are covered in §3.18).

### 3.22 Custom sales invoices (positioning)

- **Highly configurable sales invoice** layouts: optional columns/labels and add-on-driven behaviors referenced on public sales pages (“custom sales invoices” / dynamic templates narrative).

---

## 4. Bank module — features and flows

### 4.1 Account balances

- View **bank, cash, and credit-card-style ledgers** and their **balances** in one place (public bank module description combines bank/cash/**credit cards**).

### 4.2 Bank payments (cash out / expenses through bank)

- Record **bank payments** against **nominal (chart) accounts** with **amount**, **date**, **reference**, **payment mode** (modes described in public API include **Cash, Cheque, Credit Card, Offset, Online, Pay Order** and similar enumerations).
- **Multi-line vouchers** (multiple nominal splits in one payment).
- **Project** allocation per line where applicable.
- **Print:** bank voucher print and/or journal print.
- **Attachments** on payments.
- **Import** payments from Excel (grouping, templates).
- **Copy** bank payment patterns from prior vouchers.

### 4.3 Bank receipts (cash in through bank)

- Same structural capabilities as payments, for **receipts** direction.

### 4.4 Bank transfers

- Move funds between **bank/cash accounts** with voucher numbering, printing, attachments, and imports as supported.

### 4.5 Reconcile

- **Bank reconciliation** flow:
  1. Choose **bank account**.
  2. Enter **statement closing date** and **closing balance**.
  3. **Load** system transactions.
  4. **Tick/clear** items to match the statement until reconciled.

### 4.5a Import Statement

- **Import Statement** (sidebar under Bank): upload/import **bank statement** data to drive or speed reconciliation and ledger updates (separate workflow from **Excel** multi-line **bank payment/receipt** voucher imports in announcements).

### 4.6 Revaluation

- **Foreign currency revaluation** for bank accounts (paired with multi-currency feature set).

### 4.7 Multi-currency within Bank

- Currency-specific amounts and exchange rates on bank movements; ties to revaluation and realized gain/loss handling.

---

## 5. Sales module — features and flows

### 5.1 Customers (accounts receivable master data)

- Create, edit, view **customer** records.
- **Import customer** data from spreadsheet templates (public sales feature page).
- **Customer performance** evaluation (marketing; typically dashboards/reports).
- **Auto customer account numbers** (optional Smart Settings).
- **Customer groups** (referenced in advanced rights context).
- **Default customer discount %** that auto-applies to invoice lines.
- **Customer–product discount linking** (product-specific discounts per customer, including bulk invoice behavior).
- **Distribution template** extras: customer-level **trade offer** alongside discounts for schedule-3 style distribution customers.
- **Credit terms**, **credit limits**, opening balances and opening balance dates.
- **Customer also supplier** flag (dual-role party).
- **Custom fields** (multiple optional field slots on customer records and transactions).
- Up to **four assignable customer fields** plus **customer–product lines** (per customer: **product rate, quantity, discount** associations) used to drive pricing/discount behavior on documents (public sales documentation).
- **Customer table filters** by **custom fields** and **status** (public sales documentation).
- **SMS mobile** field for SMS-alerting scenarios when SMS is enabled.

### 5.2 Quotations

- **Quotations** live under **Sales**; workflow parallels **sales invoice** composition (per quotation announcement).
- Convert or progress from quotation toward order/invoice as business accepts quote (described at high level in announcements).

### 5.3 Sales orders

- Full **sales order** lifecycle with statuses (per announcements): **In Progress**, **Approved**, **Rejected**, **Invoiced**.
- **Invoiced** status can drive **automatic sales invoice** creation.
- On-screen **create invoice from order**; **multiple orders → one invoice** capability.
- **Full or partial** approval and **partial conversion** of orders (or **quotations**) into invoices as deliveries progress (public sales feature page).
- **Goods dispatch note** path: approve/issue dispatch documentation and **invoice later** when ready (public sales documentation).
- **Status** can be changed through the lifecycle as business needs change (public sales documentation).
- **Delivery note from sales order (GDNSO)** printing template family.

### 5.4 Sales invoices

- **Inline** and **distribution** invoice templates (plus legacy/default template concepts in announcements).
- Line items with **products/services**, **units**, **quantities**, **rates**, **amounts**, **discounts**, **tax codes and tax amounts**, **retail margin**, **trade offer**, **project** tagging.
- **Additional charges** and **additional deductions** mapped to **nominal accounts** (charges positive; deductions negative).
- **Width/length/area** line quantity mode.
- **Batch invoice** entry.
- **Edit after partial payment** rules: existing receipt/credit allocations remain, but new totals must remain ≥ amounts already received/offset.
- **Copy invoice** action.
- **Email** invoice to customer.
- **Attachments** on invoice.
- **Print** using configured sales invoice templates; **print designer**-style control over **which columns print** and **column titles/renames** (public sales page).
- **Import sales invoices** (and related receipt data) via **Excel** templates uploaded into the app (public sales feature page).
- **Print journal** for accounting trace.

### 5.5 Sales credits

- **Sales credit** documents (credit notes against AR). Live **Settings → Sales Printing** uses code **SC**; some older marketing/announcement text referred to sales credits as **VC**—use the **live menu** as source of truth for your clone.

### 5.6 Delivery notes

- **Delivery note** documents tied to **sales invoice** or **sales order** template channels (GDNSI / GDNSO).

### 5.7 Post-dated cheques and aggregate sales views

- **Post Dated Cheque Received:** dedicated area under **Sales** for tracking **PDCs received** from customers (distinct from immediate **Receipts**).
- **Sales All:** umbrella entry under **Sales** for cross-cutting sales work (unified lists or multi-type hub—confirm exact behavior in your build).

### 5.8 Sales receipts (customer receipts)

- Record **advance**, **partial**, or **full** customer receipts against outstanding sales (public sales documentation).
- **Bulk entry** of receipts and **Excel import** of receipt batches (public sales documentation).
- **Receipt printing** supports **multiple paper sizes** and **font/template** options (public sales documentation).
- Record customer money received; **allocation** to invoices (including FIFO assist); **credit offset** and (re)allocation **at any time** as AR changes (public sales documentation).
- **Unallocated receipts** concept (developer documentation lists **unallocated sales receipts** API).
- **Multi-invoice receipt vouchers:** public API allows **one to many** invoice lines per receipt batch (up to **50** lines per call in published API), each line optionally carrying **GST**, **withholding tax**, **discount**, **project**, and a composed **total** tied to remaining **invoice balance**; **bank account currency must match customer account currency** for the receipt (developer documentation business rules).
- **Withholding income tax** on advance receipts (dedicated announcement flow).
- **Customer advance return**: from receipts list **balance** column, **Return** action to send money back through a **bank** movement screen.
- **Voucher numbers** on listing.
- **Two-copy print** option (settings-driven).
- **Attachments**.

### 5.9 Customer ledger

- **Customer ledger** reporting and inquiry (also exposed as API concept in developer docs).
- **Sales credits** may be created/managed alongside **Invoices** (same module family; not always a separate sidebar row—see report names “Sale Invoices/**Credits**” in §10.11).

### 5.10 Sales-side operational controls

- **Filters** on invoice lists (including multi-filter pattern).
- **List filter enhancements** over time (for example dedicated “Filter Update” announcements for sales invoice search).
- **User-specific fixed sale rates** (management can lock users to product list pricing).

---

## 6. Purchases module — features and flows

### 6.1 Suppliers (accounts payable master data)

- Create, edit, view **supplier** records (parallel to customers).
- **Auto supplier account numbers** (Smart Settings).
- **Advance payments** to suppliers (common flows in announcements).
- **Notify suppliers** via **SMS** or **email** for events such as **orders**, **receipt of goods**, or **payments** (public purchases module marketing).
- **Post Dated Cheque Issued:** dedicated sidebar area under **Purchases** for **PDCs issued** to suppliers (live UI).
- **Purchases All:** umbrella entry under **Purchases** for cross-cutting purchase lists (live UI; confirm exact scope in your build).

### 6.2 Purchase orders

- Status lifecycle: **In Progress**, **Approved**, **Rejected**, **Billed**.
- **Billed** can drive **automatic supplier bill** creation.
- On-screen **create supplier bill from PO**; **multiple POs → one bill**.
- **Attachments** on POs.
- **Additional taxes** on PO lines (where enabled).

### 6.3 Supplier bills (purchase invoices / VI)

- **Import supplier bills** via spreadsheet templates for efficiency (public purchases module description).
- **Supplier bills / purchase credits** share the same document family in reporting (e.g. “Purchase Bills/**Credits**” in §10.11); UI may combine under **Bills**.
- **Batch supplier bills** screen.
- **Edit after partial payment** rules analogous to sales.
- **Width/length/area** quantity mode.
- **Attachments**.
- **Inline** vs **distribution** templates (parallel to sales enhancement announcement).
- **Supplier credits (VC)** in purchases printing taxonomy.

### 6.4 Supplier payments

- Payment recording with **allocations** (FIFO assist).
- **Withholding income tax** on advance supplier payments.
- **Supplier advance return** from payments list **Return** action.
- **Voucher numbers** on listing.
- **Two-copy print** for bill payments (side-by-side).
- **Attachments**.

### 6.5 Supplier-side documents

- **Purchase order** printing and template management within purchases printing section (paired to sales print template list).

---

## 7. Inventory module — features and flows

### 7.1 Products master record

- **Stock movement** history and **product performance** views at inventory level (public inventory marketing).
- **Stock** vs **non-stock** products.
- **Product codes** with optional **auto product codes**.
- **Categories** (auto-create category on first use where applicable).
- **Units of measure** with **multi-unit** support: different sale price, cost, and discount per alternate UM; pack sizes (large/small pack, conversion factors).
- **Pack size** handling for selling in one UM while stocking in another.
- **Bin location** field; **product image** upload.
- **Pricing fields:** sale price, cost, trade prices for purchase/sale, sale/purchase discounts (%), retail margin purchase/sale, trade offer purchase/sale.
- **Tax:** tax codes (including separate non-filer product tax code), **tax schedule** selection (references to schedule 3 vs standard schedules).
- **Purchased** flag / **preferred supplier** fields.
- Optional **shipping-style** classification on products (public API samples include shipping flags—confirm exact on-screen wording in the live product).
- **Low stock** level.
- **Opening stock** quantity/rate/date for stock items; **bulk import opening stock** tool.
- **Per-product deductions:** discount (% or amount), trade offer, retail margin (per unit or total patterns per announcements).
- **Bundle products:** selecting a bundle explodes component lines onto invoices.
- **Archive / inactive products:** hide from selection lists on sales and bills while retaining history.
- **Eight additional flexible fields** on product forms that can flow through to product-bearing transactions (per announcement).
- **Bulk tax update** via product bulk actions.

### 7.2 Stock transfer

- Move stock between **locations** / warehouses when multi-location enabled.

### 7.3 Stock adjustment

- Increase/decrease on-hand quantities with explicit adjustment workflow (including **stock adjustment out** style operations described in announcements).

### 7.4 Landed cost

- Allocate **freight, duties, shipping, delivery** and similar costs into inventory valuation after base purchase recording.
- Marketed as **automating true stock cost** and improving **profitability analysis** vs fully manual burden calculations (public module description).

### 7.5 Letter of credit

- Dedicated LC workflow: **setup**, **expenses via bank**, **expenses via supplier**, **LC products**, **cost allocation**, and **reporting** (per LC announcement).

### 7.6 Projects (inventory-area entry point)

- **Project accounting** when enabled: **unlimited projects** in core descriptions, while **public pricing pages** also describe **tier caps** on maximum projects (examples: **10 / 15 / 20 / 25** projects by package) with **contact sales** for expansion—capture the **exact** rule from your target tier in implementation.
- **Profit and loss** (and **nominal activity**) visibility per project; reports for **one or many** projects at a time (public module description).
- Projects appear as selectable codes on operational lines.

### 7.7 Multi-unit (feature area)

- Documented as its own support topic alongside multi-UM on products.

### 7.8 Batch and expiry

- **Batch** tracking on purchase and sale with selectable batch at sale time.
- **Expiry** tracking for perishables.
- Batch/expiry usable in **assembly** and standard inventory flows.

---

## 8. Fixed assets module (optional add-on)

- **Register and track** a range of **fixed assets** in a dedicated module (public pricing/feature pages).
- **Import and export** of fixed asset data for bulk maintenance.
- **Lifecycle and valuation** views to support decisions on holding and retiring assets (described at marketing level as lifecycle/assessment support).

---

## 9. General ledger, journals, and budgets

### 9.1 Nominal codes (chart of accounts)

- Logical hierarchy: **Category → Section → Nominal account** (each nominal is a **GL account** row used across the product).
- **Auto nominal codes** optional (**Smart Settings** — §12.2.8 **Nominal auto code**).
- **Settings** mega-menu exposes three related links in the same column (**§12.1**): **Chart of Account** (full tree browser — **§9.1.1**), **Nominals**, and **Section Management** (**§9.1.4** — **section** rows under each **category**). **Parity:** confirm whether **Nominals** opens the same surface as **Chart of Account** or a filtered / alternate nominal workspace (**§9.1.3**).

#### 9.1.1 Chart of Account (live — `Home / Chart of Account`)

**Entry:** **Settings** mega-menu → **Chart of account** group → **Chart of Account** (§12.1). **Breadcrumb:** **Home / Chart of Account**. **Do not** paste tenant **account codes** or **names** from screenshots into this catalog.

**Toolbar / chrome:** **+ Nominal account** (green) — opens add flow (**§9.1.2**); **bulk delete** (trash icon—typically uses row **checkboxes**); **filter** (icon control); **Search** box; **Show *n* entries** page size.

**Grid:** **Checkbox** column; **Code**; **Nominal account** (display name); **Action** — **Edit** with **dropdown** (confirm delete / view / move in-app).

**Hierarchy presentation:** accounts render under **group headers** (blue band style in capture) for **top-level categories** (with **account counts** in parentheses), nested **section** sub-headers (again with counts), then **leaf** nominal rows—supports expand/collapse or static grouping (verify interaction).

#### 9.1.2 Nominal Account New (modal)

Opened from **+ Nominal account** on the chart page.

- **Required:** **Category** (dropdown); **Section** (dropdown — options come from **Section management** — §9.1.4); **Nominal account** (name text — placeholder **Name** in capture).  
- **Code** — text field; may be **read-only / greyed** when **auto nominal** numbering supplies the code from **Smart Settings** (§12.2.8).  
- **Description** — optional text.  
- **Deduction and charge** — checkbox (marks nominal for use in **deduction/charge** style postings—confirm business rule in help).  
- **Right pane — Existing nominal accounts:** small **Name** / **Code** reference grid (intended to show **siblings** under the chosen category/section to avoid duplicates—confirm when it populates).  
- **Actions:** **Cancel**; **Save and close** (green).

#### 9.1.3 Nominals link (parity)

The **Nominals** menu item (§12.1) is listed **separately** from **Chart of Account**. Inventory whether it is an **alias route**, a **flat nominal list**, or **import/export** surface distinct from the hierarchical chart.

#### 9.1.4 Section Management — Section Listing & Section New (live)

**Entry:** **Settings** mega-menu → **Section Management** (§12.1). **Breadcrumb / title:** **Home / Section Listing** with page heading **Section listing** (casing may vary). **Purpose:** maintain **section** records (the middle layer under **category**, above **nominal accounts** — §9.1). **Do not** paste tenant **section codes** or **names** from screenshots into this catalog.

**Toolbar / chrome:** **+ Add new** (green) — opens **Section new** modal; **export** icons (**PDF** and **Excel** in one capture); **bulk delete** (trash in another capture—confirm which icons appear together in your build); **Search** above the grid.

**Grid:** **Checkbox** column (select rows—including **category** header rows in one capture—for bulk actions; verify selection rules); **Section** (label); **Code** (numeric **section** code); **Reorder** — **Up** / **Down** controls (green **up**, red **down**) to move a section within its ordering scope; **Action** — **Edit** (link).

**Hierarchy:** **Category** group headers with **counts** in parentheses; nested **section** rows listed beneath each category (same visual language as **Chart of Account** — §9.1.1).

**Section new** (modal — title **Section new** in capture): **Category** * (dropdown); **Section** * (name text — placeholder **Name**); **Code** (often **read-only** / greyed—likely driven by **section auto** numbering or category rules — align with **Smart Settings** section-code policies if any); **Existing sections** — right-hand reference panel (**Section** / **Code** columns, populates when category context is chosen—confirm); **Cancel**; **Save and close** (green).

### 9.2 Journal entries

- **General journal** with **journal IDs** on the listing (see **§9.2.1** for live list UX).
- **Manual journals** with traditional debit/credit presentation available via printing.
- **Attachments** on journals.
- **Copy** prior journals.

#### 9.2.1 Journals list (live — `Home / Journals`)

**Entry:** **Settings** mega-menu → **Journals** column → **Journals** (§12.1). **Breadcrumb:** **Home / Journals**. **Do not** paste live **amounts**, **dates**, or **journal IDs** from tenants into this catalog.

**Toolbar:** **+ Add new** (green) — create a journal voucher; **export to spreadsheet** (icon—confirm whether export is filtered list or selection); **print** (list print—distinct from per-voucher **Journal** templates in §12.1 / §3.7); **bulk delete** (trash icon—typically requires **checkbox**-selected rows; confirm **lock date** and status rules).

**Filters:** **Nominals** dropdown (**Select** placeholder in capture); **Ref no.** text box; **Date range** preset (e.g. **All dates**); **Clear**; **Show *n* entries** page size.

**Grid:** checkbox column; **Journal ID** (numeric, **link** to voucher); **Date**; **Ref. no.** (short narrative, e.g. **Opening balance**-style text in live data); **Total** (voucher-level amount in capture); **Action** — **View** plus **dropdown** (confirm edit / delete / print line items in-app).

**Footer:** “Showing *x* to *y* of *z* entries” and **pagination**.

### 9.3 Budget

- **Budget module** (commonly an add-on): create **multiple budgets**; **import/export** budget data; **compare budget to actual** at **company** level and/or by **project(s)** (public module description).

### 9.4 Taxes and year-end configuration

- **Functional home:** **Settings → Taxes and Year End** (live breadcrumb **Home / Taxes and Year End** — full field layout in **§12.12**). There you maintain **fiscal year end**, **tax-on-document display** toggles, **GST / additional invoice tax / FED** rate grids bound to **regions** and **nominal accounts**, **WHT** rate lines, and the **tax region** master list. **Do not** paste live **rates, codes, or COA numbers** from tenants into this catalog.
- **Distinction:** **Smart Settings** (§12.2.8) configures **automatic codes** for WHT/GST/ADT/FED entities; **Taxes and Year End** configures **rates, labels, and where each tax applies** on documents.

### 9.5 Lock date

- Global and **per-user** lock enforcement on historical edits/deletes.

---

## 10. Reports and business analysis

### 10.1 Standard reports

- Marketing and support describe a **large standard report library**; different public pages quote different magnitudes (**200+** unique reports in one area, **300+** in hero marketing — treat as **order-of-hundred breadth** until enumerated from the live product).
- Reports are **filterable** and **exportable** (for example **Excel** with **transaction type** labeling).

### 10.2 Report UX

- **Hyperlinks** from report cells into underlying detail records.
- **Combined account reports** refresh (customer/supplier reports reorganized across **Sales & Customer**, **Debtors & Recovery**, **Purchases & Supplier**, **Creditor and Payments** sections).
- **Favourite / bookmarked reports** area for quick access to frequently used reports (public pricing/report module description).
- **Spelling:** live **Reports** hub uses **Favorites** (US spelling); **Analytical Reports** hub uses **Favourites** (UK spelling)—same concept, **star** toggle on each report row/card.

### 10.3 Analytical reports (module + live hub layout)

- Dedicated **Analytical Reports** area (top-level sidebar entry): large set of **data-style** reports (public materials cite **30+** / **33** reports; live UI uses numeric IDs in the **200–500** range for some entries).
- **Search** across reports; **Expand all** (toolbar control) for accordion UX; **star** to add reports to **Favourites**.
- **Live category list** (accordion headers): **Favourites**, **Sales and Recovery**, **Sale Order**, **Purchases and Payments**, **Purchase Order**, **Cash and Bank**, **Product and Services**, **Management** *(further categories may exist when scrolled or when modules are enabled)*.
- **Examples under Cash and Bank:** `300` Bank Payment and Receipts Data; `477` Bank Receipt Nominal Summary By Year; `475` Bank Payment Nominal Summary By Year.
- **Example in Favourites:** `272` Bills Data.

### 10.4 Tax reporting

- Examples explicitly named in announcements:
  - **GST Sale Invoices Details** (GST vs additional tax columns)
  - **GST Return Summary** updates
  - Broader **sales tax** report suite adjustments for non-filer elements.

### 10.5 Assembly reports

- Examples named:
  - **Job Cost Summary By Finished Product**
  - Additional assembly report additions over time.

### 10.6 Project reports

- Examples named:
  - **Project Payments** report (supplier/cashbook expenses by project, bank ledger context).

### 10.7 Debtors and recovery

- Examples named:
  - **Sales Recovery Summary (By Date)** with **withholding income tax** breakdown elements.
  - Additional **sales recovery** reports in “new reports” bundles.

### 10.8 Bank activity

- **Bank activity summary** style reporting referenced alongside sales recovery additions.

### 10.9 Dashboard (live widget model)

The **Dashboard** home aggregates operational KPIs and deep-links into **Reports**. Structure below is from **live product usage**; widgets show **titles**, **primary totals**, optional **sub-tables**, period toggles (e.g. **12 months**), and **View report** / chart links.

**Accounts receivable**

- **Account Receivable Summary:** **Total receivable**; table **Unpaid invoices** with **balance** columns and **aging buckets**: **Older**, **Current**, **1–7 days**, **8–14 days**, **15–21 days**, **22–28 days**, **Future** (each row shows **document count** in parentheses and **balance**); **View report**.
- **Account Receivable Top 10:** ranked **customers** with **balance** (top debtors snapshot).
- **Account Receivable Watchlist:** configurable or pinned **AR** watch list (names + balances).

**Accounts payable**

- **Account Payable Summary:** **Total payable**; **Unpaid bills** with the **same aging bucket** pattern as AR; **View report**.
- **Account Payable Top 10:** ranked **suppliers** with **balance**.
- **Account Payable Watchlist:** **AP** watch list.

**Banking**

- **Bank balances:** table of **bank / cash / e-wallet** style accounts (each line: **display name**, **nominal code in parentheses**, **balance** in base currency).
- **Bank balances watchlist:** subset of accounts for quick monitoring.
- **Bank cash flow all:** chart or summary for **12 months** (toggleable period where shown).
- **Bank cash flow watchlist:** watch-listed cash-flow view.
- **Monthly bank balance all:** **12-month** series.
- **Monthly bank balance watchlist:** watch-listed monthly balance trend.

**Inventory**

- **Products** strip: **quantity** in scope; counts for **low stock**, **out of stock**, **oversold**, **in stock** (aggregate inventory health).

**Performance (financial year)**

- **Sales:** **this financial year** total.
- **Expenses:** **this financial year** total.
- **Profit & loss:** **this financial year** with **net profit**, **total income**, **total expenses**; **View report**.

### 10.10 Reports hub — live navigation tree

The **Reports** screen has title **Reports**, **Search reports** (top right), and a **left navigation** tree. Expandable groups use chevrons; selecting a **leaf** (or subgroup) loads a **grid of report cards** in the main pane (two columns, **numeric ID**, **title**, **star** for Favorites).

#### 10.10.1 Top-level categories (live)

- **Favorites**
- **Sales** *(expandable — see §10.10.2)*
- **Purchases** *(expandable — see §10.10.3)*
- **Bank**
- **Inventory** *(expandable — see §10.10.4)*
- **Financial** *(expandable — report IDs not yet captured)*
- **Assembly**
- **Projects**
- **Taxes** *(expandable — see §10.10.5)*
- **Budget**
- **Fixed Assets**
- **Consolidation**

#### 10.10.2 Under **Sales** (live subgroups)

- **Sales and Customer** *(full report list — §10.11.2)*
- **Accounts Receivable** *(reports not yet listed in this doc — capture IDs from live app)*
- **Quotations**
- **Sale Order**
- **Goods Dispatch Note**
- **Combined Account**

#### 10.10.3 Under **Purchases** (live subgroups)

- **Expenses and Suppliers**
- **Accounts Payable**
- **Purchase Order**
- **Goods Receipt Note**

#### 10.10.4 Under **Inventory** (live subgroups)

- **Products** *(full report list — §10.11.3)*
- **Letter of Credit** *(LC-related reports under Reports; complements operational LC module — §7.5)*

#### 10.10.5 Under **Taxes** (live subgroups)

- **Sales Tax**
- **ADT Tax**
- **FED Tax**
- **Withholding Tax (Customer)** *(label truncated in UI as “Withholding Tax (Cust…)”)*
- **Withholding Tax (Supplier)** *(label truncated as “Withholding Tax (Sup…)”)*
- *(Further tax subfolders may exist when scrolled or when regimes differ — verify in tenant.)*

---

### 10.11 Inventoried standard reports (live IDs — partial catalog)

Only groups **fully captured** from your **Reports** screenshots are listed below. **Bank**, **Financial**, **Assembly**, **Projects**, **Budget**, **Fixed Assets**, **Consolidation**, and other **Sales / Purchases** subfolders still need the same treatment (see §15).

#### 10.11.1 Favorites (starred mix — cross-module)

| ID | Report name (as shown) |
|----|-------------------------|
| 028 | Sale Invoices/Credits (By Date) |
| 034 | Customer Statement |
| 047 | Customers Balances Summary |
| 141 | Sale Invoices/Credits with Recovery Detail (By Date) |
| 182 | Customer Performance |
| 048 | Purchase Bills/Credits (By Date) |
| 051 | Purchase Bills/Credits Detail (By Supplier) |
| 054 | Supplier Statement |
| 067 | Suppliers Balances Summary |
| 238 | Bills/Credits Detail (By Date/Product/Project) |
| 071 | Bank Payments |
| 148 | Stock Valuation |
| 085 | Product Sale Detail (By Product) |
| 087 | Product Purchase Detail (By Product) |
| 162 | Product Performance |

#### 10.11.2 Sales → **Sales and Customer** (complete list from live UI)

| ID | Report name (as shown) |
|----|-------------------------|
| 028 | Sale Invoices/Credits (By Date) |
| 029 | Sale Invoices/Credits (By Customer) |
| 030 | Sale Invoices/Credits Details (By Date) |
| 031 | Sale Invoices/Credits Detail (By Customer) |
| 032 | Sale Summary (By Date) |
| 033 | Sale Summary (By Customers) |
| 034 | Customer Statement |
| 035 | Customer List |
| 141 | Sale Invoices/Credits with Recovery Detail (By Date) |
| 142 | Sale Invoices/Credits with Recovery Detail (By Customer) |
| 143 | Customer Statement Outstanding Items |
| 144 | Sale Invoices Statement Detail |
| 145 | Customer Products |
| 160 | Customer Statement (Invoice Detail) |
| 178 | Sale Invoices/Credits Detail (By Customer/Product) |
| 182 | Customer Performance |
| 240 | Sales/Credits Detail (By Date/Product/Project) |
| 241 | Sales/Credits Detail (By Customer/Product/Project) |
| 243 | Customer Statement (Style One) |
| 245 | Sales Detail (Statement Style) |
| 246 | Customer Statement (Style Two) |
| 311 | Customer Field Activity Summary |

#### 10.11.3 Inventory → **Products** (complete list from live UI)

| ID | Report name (as shown) |
|----|-------------------------|
| 078 | Products List |
| 079 | Price List |
| 080 | Stock Quantity |
| 081 | Product Activity |
| 082 | Out of Stock |
| 083 | Low Stock |
| 084 | Product Sale Detail (By Date) |
| 085 | Product Sale Detail (By Product) |
| 086 | Product Purchase Detail (By Date) |
| 087 | Product Purchase Detail (By Product) |
| 088 | Product Sale Summary |
| 089 | Product Purchase Summary |
| 148 | Stock Valuation |
| 149 | Product Activity Summary |
| 162 | Product Performance |
| 164 | Product Stock (By Location) |
| 173 | Opening Stock |
| 174 | Stock Movement |
| 175 | Advanced Stock Quantity |
| 181 | Multi-Unit Price List |
| 185 | Sale Summary (By Field) |
| 206 | Stock Transfer Detail |

### 10.12 Standard report runner — screen pattern (live)

When a report (e.g. **Products List**) is opened, a typical layout includes:

- **Report criteria** (collapsible panel): **filters** such as **Product status**, **Type**, **Category** (dropdowns; values like **All** or a specific category); primary action **Run report** (e.g. green button) to refresh the dataset.
- **Report-specific settings** entry (e.g. **gear** + “Settings”) for layout or defaults tied to that report.
- **Toolbar** on the result pane: **column / layout** control, **print**, **export to Excel** (or equivalent spreadsheet export).
- **In-table search** (“Search:” above the grid).
- **Data grid** with **sortable** column headers (sort arrows), alternating row styling, and columns appropriate to the report (e.g. type, product code, name, category, pricing, unit, notes).

---

## 11. Assembly (manufacturing / kitting)

### 11.1 Concepts

- **Assembly templates** and **assembly jobs**.
- Raw material and overhead allocation to **finished goods** with **job costing**.
- **Approve/finish** style workflow permissions (role rights include **Finish**, **Print**, **Print Cost** specific to assembly).

### 11.2 Assembly upgrades (recent)

- **Smart filters** for customizable assembly views.
- Other assembly UX upgrades described at high level in upgrade announcements.

### 11.3 Batch and expiry integration

- Batch/expiry tracked through assembly where business requires it.

---

## 12. Settings, authorization, and administration (company-level)

### 12.1 Settings menu — live mega-menu (modal overlay)

The **Settings** experience is a **modal overlay** (not a single long page): **blue column headings**, link groups, **close** control, and a **right-hand rail** for session/tenant actions. Below is the **structure captured from live UI** (exact grouping labels as shown).

#### Column — journals, chart of accounts, users, controls

| Group | Links / items |
|--------|----------------|
| **Journals** | **Journals** (GL listing and entry — §9.2.1) |
| **Chart of account** | **Chart of Account** (hierarchical COA browser — §9.1.1) |
| **Nominals** | **Nominals** (separate entry from chart — relationship §9.1.3) |
| **Section Management** | **Section Management** — **Section listing** CRUD & reorder (**§9.1.4**) |
| **User & Roles** | **Users Management** (§12.3); **Roles Management** (§12.4); **Dashboard Management** (configure dashboard widgets / permissions—align with §10.9) |
| **Lock Date** | **Lock Date** (§9.5) |
| **OP Methods** | **OP Methods** *(abbreviation as in UI; confirm business meaning in your build—e.g. opening / operational posting options)* |
| **Log Management** | **Log Management** — **User log** audit viewer (**§12.15**); complements §3.4 |

#### Column — general application settings

| Group | Links / items |
|--------|----------------|
| **Settings** | **Smart Settings** (§12.2); **Taxes and Year End** (§12.12); **Business Information** (§12.13); **Filters Management**; **Column Management**; **Content Settings** (§12.14) |
| **Recurrence** | **Missed Recurrence** (exception handling for scheduled / recurring transactions — §3.3) |
| **Email & SMS** | **Email Settings**; **Sent Emails** (outbound message log — complements §3.6 / §3.19) |

#### Columns — printing configuration (document templates)

| Group | Document print targets (codes as shown in UI) |
|--------|-----------------------------------------------|
| **Sales Printing** | **SI** Sales Invoice; **SC** Sales Credit; **SO** Sales Order; **SR** Sales Receipt; **PDCR** Post Dated Cheque Received; **GDNSI** / **GDNSO** Delivery Notes; **CUS** Customer |
| **Purchases Printing** | **VI** Supplier Bill; **VC** Supplier Credit; **PO** Purchase Order; **VP** Bill Payment; **PDCI** Post Dated Cheque Issued; **GRNPO** Goods Receipt Note (PO); **GRNVI** Goods Receipt Note (VI) |
| **Journal Printing** | **Journal** |
| **Bank Printing** | **Bank** |
| **Other Printing** | **Assembly**; **Stock Adjustment**; **Stock Transfer**; **User Log** |
| **Project Printing** | **Project** |

#### Right rail — session & tenant

- **Switch Company** (multi-company / multi-book switching — §2.3).
- **Profile**
- **Change Password**
- **Dark Mode** (theme toggle)
- **Logout**

#### Cross-reference to documentation gaps

Items from public **support** maps that are **not** visible as top-level links in this capture (for example **Budget**, **Location**, **Authorisation**, **Advance users** as named groups) may live **inside Smart Settings**, **Business Information** (§12.13), or **sub-screens**—capture drill-downs when cloning (see §15).

Public help still uses names like **Budget**, **Authorisation**, **Advance Users**, **Location**, **Nominal codes**, **User roles and rights**—treat **this §12.1 layout as authoritative for the live mega-menu** and map older article titles as **aliases** until each is traced to a concrete link.

### 12.2 Smart Settings (live — `Home / Smart Settings`)

Dedicated page (breadcrumb **Home / Smart Settings**): **accordion** sections, **Cancel** / **Save** on each expanded block (green **Save**), some inner panels with their own **Save**. Captured structure below; **do not store real PINs, serials, or prefixes** in specs—describe fields only.

#### 12.2.1 Accordion index (all section titles from live UI)

1. **Others**  
2. **Sales**  
3. **Purchases**  
4. **Bank**  
5. **Fixed Assets**  
6. **E-Signatures**  
7. **Product Description**  
8. **Template / Draft**  
9. **Last Rate**  
10. **Customer Auto Account No.**  
11. **Supplier Auto Account No.**  
12. **Product Auto Code**  
13. **Location Auto Code**  
14. **Project Auto Code**  
15. **WHT Auto Code**  
16. **GST Auto Code**  
17. **ADT Auto Code**  
18. **FED Auto Code**  
19. **Nominal Auto Code**  
20. **Currency & Time Zone**

#### 12.2.2 **Others** — global feature toggles and defaults

- **Boolean toggles** (multi-column), including: **Set customer as supplier**; **Warning on over sale (order)** / **(invoice)**; **View product last sale rate**; **Round off sales**; **Nonstock transfer**; **Auto payment offset**; **Projects accounting**; **Apply credit limit**; **Apply SO credit limit**; **Customer WHT**; **Quotations**; **Customer products**; **POS invoices**; **Transaction notes**; **Fine daily** / **Fine percentage** (late-payment fine behavior—paired with product/charge selectors).
- **Enter PIN** field for protected changes (**never commit real PIN values** to repositories).
- **Dropdowns:** product used for **late payment fine**; **additional charges**; **additional deductions**; **invoice template** (e.g. **Inline**); **batch expiry date print format** (e.g. ISO date format string); **supplier statement template**; **customer statement template**.

#### 12.2.3 **Sales**, **Purchases**, **Bank**, **Fixed Assets** — smart filters & docs

Common pattern when expanded:

- **Smart Filter 1–4** — define labels for the four **filter** slots on documents (aligns with **Filter1–4** on invoices/orders in API and UI).
- **Smart Doc 1–4** — define labels for four **smart document number** slots (**SmartDocNo** fields).
- **Default note blocks:**  
  - **Sales:** **Sales invoice notes**, **Sales order notes**, **GDN notes** (goods delivery note), **Quotations notes**.  
  - **Purchases:** **Purchase order notes** (plus smart filter/doc fields).  
  - **Bank:** at least **Smart Filter 1–4** (one live capture shows **only** these four fields—no **Smart Doc** row in view; confirm whether Bank omits smart docs or they appear below the fold).  
  - **Fixed assets:** smart filter + smart doc quartets.

#### 12.2.4 **E-Signatures**

- Table: **ID**, **Name**, **Signature** (file **Upload**), **Action** (**View** / **Delete**); **+ Add more** rows.

#### 12.2.5 **Product Description** (line layout on documents)

- Grid columns: **Display name**, **Label**, **Width**, **Transaction type** (multi-assign).  
- Primary row maps the main **product description** column to types **SI, SC, SQ, VI, VC, PO** (**SQ** = **sales quotation**).  
- Optional extra lines (**Text 1** … **Text 6**) for additional description columns with configurable width.

#### 12.2.6 **Template / Draft**

- Matrix: **module** × **Template** checkbox. Modules: **Journal**; **Bank payments**; **Bank receipts**; **Bank transfers**; **Bills**; **GRN**; **GDN**; **Sale invoices**—enables template/draft capture path per module (see **§3.3**–**§3.4**).

#### 12.2.7 **Last rate**

- Grid: document **type** rows (**PO, QO, SC, SI, SO, VC, VI**) × **Add/Edit** and **View** checkboxes controlling who may see or change **last rate** data per document family (**QO** appears alongside **PO** / quotation-order style docs—confirm exact doc name in UI tooltips).

#### 12.2.8 **Auto account no. / auto code** blocks

For **customer**, **supplier**, **product**, **location**, **project**, **WHT**, **GST**, **ADT**, **FED**, and **nominal** entities:

- **Enable** checkbox; **auto start serial number**; **prefix** field; optional **Advance** panel (e.g. **update all** existing codes—**non-reversible** warning shown for bulk FED code rewrite).  
- Section-level **Save** on each auto-code card.

#### 12.2.9 **Currency & time zone**

- **Base currency** (country/currency selector).  
- **Time zone** (offset + IANA-style region).  
- **Date format** (e.g. `dd/mm/yyyy`).  
- Footer **Cancel** / **Save** for the whole page where shown.

### 12.3 User management (live — `Home / Users`)

Entry from **Settings** mega-menu → **User & Roles** → **Users Management** (§12.1). **Breadcrumb:** **Home / Users**. **Do not** record real **names, emails, or phones** from tenants in this catalog.

#### 12.3.1 Users list

- **Header actions:** **Add new** (green); **Manage roles** (navigates to role administration—§12.4).  
- **Table chrome:** **Show *n* entries** dropdown; **Search** box.  
- **Columns:** **Name**, **Phone**, **Email**, **Type** (e.g. user vs admin category), **Role** (assigned permission set), **Status** (e.g. **Active**), **Action** (**Edit** with **dropdown** for further row actions—confirm full menu in-app, e.g. delete / deactivate).  
- **Footer:** “Showing *x* to *y* of *z* entries” and **pagination**.

#### 12.3.2 Add user (`Home / Users / Add User`)

- **Breadcrumb:** **Home / Users / Add User**. **Actions:** **Cancel**; **Save and close** (green).  
- **Required fields** (red asterisk in UI): **First name**, **Last name**, **Email**.  
- **Optional / policy:** **Mobile number**.  
- **Type** — dropdown (distinguishes **admin**-class vs standard **user**-class accounts in capture; exact enum labels in your build).  
- **Restrict via IP address** — free text, **comma-separated** allowlist.  
- **Dashboard** — dropdown to pick a **default dashboard** profile for the user (**Select** placeholder when unset).  
- **Active** — checkbox (defaults **on** in capture) to enable or hold the account.  
- **Role assignment:** the **Users** list shows a **Role** column; the **Add user** capture does **not** show a **role** picker—confirm whether **role** is set on this form (scroll / tab), only on **edit user**, or via a separate step (§15).

#### 12.3.3 Edit user and field locks (published behavior)

- For **non-admin** users, product documentation describes **per-user locks** on: **sale rate**, **discount**, **RM** (retail margin), **TO** (trade offer), **bundle quantity**, **GST on sales**, **GST on bills**, and **which bank / cash books** the user may use—capture the exact **edit user** form layout in your tenant.

### 12.4 Roles management (live — `Home / Roles` …)

Entry from **Users** screen **Manage roles** and/or **Settings → User & Roles → Roles Management** (§12.1). **RBAC** model: users carry a **role**; permissions live on the **role** definition.

#### 12.4.1 Add role (`Home / Roles / Add Role`)

- **Breadcrumb:** **Home / Roles / Add Role**. **Role name** — required. **Save and close** (green, top right in capture).  
- **Select rights** — long **hierarchical** list: each major line has a **checkbox** and often a **“+”** expander to reveal **sub-rights** (typical patterns: **view / add / modify / delete / share / print / import / approve**—confirm exact verbs per node in-app; public help cites **View**, **Modify**, **Add**, **Delete**, **Share**).  
- **Assembly**-specific rights called out in help: **Finish**, **Print**, **Print cost**; product evolution also added explicit **Print** and **Import** allocation in announcements.

#### 12.4.2 “Select rights” top-level modules (live labels)

When creating a role, the tree roots include at least: **Settings**; **Bank**; **Sales**; **Purchases**; **Inventory**; **Letter of credit**; **Vehicles**; **Projects**; **Assembly**; **Landed cost**; **Budget**; **SMS**; **Fixed assets**; **Consolidation**—some nodes may be **leaves** (checkbox only) while others **expand** into submodule rights.

#### 12.4.3 Report-only permission groups (live labels)

Separate from transactional modules, the role editor lists **report access** buckets so a role may **view** report suites without full module write access. Captured group titles include: **Sales and customer reports**; **Accounts receivable**; **Quotations reports**; **Sale order reports**; **Goods dispatch note reports**; **Expenses and suppliers reports**; **Combined account reports**; **Accounts payable**; **Purchase order reports**; **Goods receipt note reports**; **Cash and bank reports**; **Products reports**; **Withholding tax (customers) reports**; **Withholding tax (suppliers) reports**; **Sales tax reports**; **ADT tax reports** *(one capture spelled **ADIT**—treat as label drift vs **ADT**; confirm in UI)*; **FED tax reports**; **Management reports**; **Management reports (cash accounting)**; **Project reports**; **Assembly reports**. Further leaves may appear when expanded or when modules are licensed.

### 12.5 Advance users (premium-style module)

- **Allocate customers, suppliers, and products** visible to each user for sales/purchases operations and reporting (data visibility fence beyond module on/off).

### 12.6 Authorisation

- **Authorisation module** (often an add-on): configurable **approval workflows** so designated approvers validate transactions before they take full effect; described as applicable across **most financial activities** for control, accuracy, and fraud reduction.
- Pairs with **draft and approve** behaviors on transactional documents (see §3.4).

### 12.7 Location

- **Locations** listing with default **main warehouse**; add new locations for **multi-location inventory**.

### 12.8 Printing (configuration)

- All **per-document print template** targets exposed in the Settings menu are listed under **§12.1** (**Sales / Purchases / Journal / Bank / Other / Project** printing groups).
- Older announcements (§3.7) use the same **SI / SC / …** vocabulary; **PDCR**, **PDCI**, **VP**, **GRNPO**, **GRNVI**, and **CUS** appear explicitly in the **live printing** menu.

### 12.9 Advance users screen (support label)

- Distinct **Advance Users** article path under settings/support for advanced user controls.

### 12.10 User roles and rights (support label)

- Overlapping but separate article trail for **user roles and rights** management content.

### 12.11 Policies and compliance artifacts (customer-facing)

- Public site includes **privacy**, **refund/cancellation**, **payment policy**, **terms of service**, **FAQs**, **support**, **tutorials**, **case studies**, **contact**—these are part of the commercial product surface around the accounting app.

### 12.12 Taxes and Year End (live — `Home / Taxes and Year End`)

Dedicated **Settings** page (§12.1 **Settings** column)—**not** inside the **Smart Settings** accordion. **Breadcrumb:** **Home / Taxes and Year End**. **Save** appears at **page** level (e.g. top right); **collapsible sections** also carry their own **Cancel** / **Save** (and tables use **+ Add more**). Treat **section Save** vs **global Save** scope as a parity detail to verify in-app.

#### 12.12.1 Year end

- **Year end date** — dropdown selecting the company **financial year-end** (calendar date).

#### 12.12.2 Tax display settings

- Table: **Description** | **Label** (text shown on documents) | **Supplier** (checkbox) | **Customer** (checkbox).  
- **Row families** (as labeled in UI): **GST on invoice**; **ADT on invoice**; **FED on invoice**; **WHT (withholding income tax)**; **GST withheld**. Enables or labels each tax **lane** for **supplier-side** vs **customer-side** documents independently.

#### 12.12.3 GST rates (and same-shaped **additional invoice tax** / **FED** blocks)

- Repeated **rate table** pattern: **Region** (dropdown, keyed to **Tax regions**), **Region code**, **Tax code**, **Tax rate (%)**, **Add. tax rate (%)**, **Account** (chart-of-accounts / nominal link), **Print label**, **Status** (e.g. active), **Actions** (edit / delete). **+ Add more** rows.  
- **Section titles:** **GST rates**; **FED rates**; and an **additional invoice tax** block captioned **ADT rates** in one capture and **AST rates** (*additional sales tax*) in another—**confirm the live string** in your build (may vary by localization or version).

#### 12.12.4 WHT rates

- Table: **Tax name**, **Tax code**, **Tax rate (%)**, **Actions**; **+ Add more**.

#### 12.12.5 Tax regions

- Master grid: **Region name**, **Region code**, **Actions**; **+ Add more**. Feeds the **Region** dropdowns in §12.12.3. Regional seed data is **localization-dependent**—capture your tenant’s list from the app, not from screenshots in this repo.

#### 12.12.6 Relation to Smart Settings auto codes

- **Taxes and Year End** (this section): **rates**, **display toggles**, **regions**, **nominal links** for posting/printing.  
- **Smart Settings →** **WHT / GST / ADT / FED auto code** (§12.2.8): **serial numbering / prefixes** for those code entities. Both are required for end-to-end tax behavior.

### 12.13 Business Information (live — `Home / Business information`)

Dedicated **Settings** page (§12.1 **Settings** column)—**not** part of the **Smart Settings** accordion. **Breadcrumb** in capture: **Home / Business information** (casing may vary). **Purpose:** company **legal/trading identity**, **contact**, **branding**, and **registration IDs** used on documents and integrations.

#### 12.13.1 Form layout (three columns)

- **Column 1 — address block:** **Business name**; **Business address line 1** through **Business address line 5**; **Branch name**.  
- **Column 2 — contact & brand:** **Phone number**; **Mobile number**; **Email address**; **Website address**; **Logo** — preview area, **Remove logo**, **Choose file** upload, stated **maximum upload size** (e.g. **1 MB** in capture).  
- **Column 3 — registrations & print scope:** **CNIC**; **STN**; **NTN**; **Apply on all prints** (checkbox — when set, business block / logo apply across configured printouts).

#### 12.13.2 Footer actions and subscription strip

- **Cancel** and green **Save**.  
- **Read-only subscription / account strip** (placement adjacent to footer in capture): labels such as **Account No.** and **Renewal date** for the Fast Accounts subscription—**do not** copy live subscription identifiers or dates into this catalog.

### 12.14 Content Settings (live — `Home / Content Settings`)

Dedicated **Settings** destination (§12.1 **Settings** column). **Breadcrumb:** **Home / Content Settings**. **Layout:** **left navigation tree** + **main workspace** (not the Smart Settings accordion).

#### 12.14.1 Sidebar — top-level groups

- **Forms** — *(structure not expanded in current catalog screenshots.)*  
- **Menu** — *(same.)*  
- **Listing** — expandable; when open it lists **Sales Listing**, **Project Listing**, **Bank Listing**, **Purchase Listing**, **Inventory Listing** (labels as shown in live UI).

#### 12.14.2 Listing → Sales Listing (card hub)

Main pane shows **one card per** configurable **sales-related grid**. Each card’s copy states that administrators can **reorder columns**, **rename labels**, and **choose which columns show or hide**. **Targets captured:**

- **Sale invoice listing**  
- **Post dated cheque received listing**  
- **Customers listing**  
- **Sale receipts listing**  
- **Sale orders listing**  
- **Advanced sale invoice listing**

Selecting a card drills into that listing’s column editor (pattern aligned with §12.14.3—confirm button labels per card in-app).

#### 12.14.3 Listing → Inventory Listing → Product Listing

- **Section title:** **Product listing** (blue header in capture).  
- **Actions:** **Reset** (revert layout—red control in capture); **Update** (persist changes—green).  
- **Row editor:** scrollable list of **fields**; each row has a **drag handle** (reorder), **field name**, **Active** / **Inactive** visibility toggle, and **Edit** (pencil) for field-level options.  
- **Sample column keys** visible in one capture (not necessarily exhaustive): **Code**, **Name**, **Type**, **Category**, **Sale Info.**, **Notes**, **Unit**, **Stock account**, **Expense account**, **Income account**, **Cost**, **Weight**, **TP sale**, **TP purchase**, **TQ sale**, **TQ purchase**—treat **TP** / **TQ** as **UI labels** until confirmed via in-app tooltips (do not assume they equal **QO** or other doc-type abbreviations from §14).

#### 12.14.4 Other branches (parity)

- **Project**, **Bank**, and **Purchase** listing branches appear in the sidebar; **Forms** and **Menu** roots exist—capture each drill-down for the same **reorder / rename / visibility** (and any **Reset** / **Update** naming) conventions.

### 12.15 Log management — User log (live — `Home / User Log`)

**Settings** mega-menu → **Journals** column → **Log Management** (§12.1). **Breadcrumb:** **Home / User Log**. **Purpose:** read-only **audit trail** of **sign-ins** and **transactional events** with attribution. **Distinct from** the **User log** **print template** under **Other Printing** (§12.1)—that configures a **paper/PDF layout**; this section is the **on-screen log browser**.

#### 12.15.1 Filters

- **Type** — dropdown (e.g. restrict to **log in** / **log out** vs **transaction type** families—confirm full enum in-app).  
- **User** — dropdown (filter by **user** or equivalent scope shown in UI).  
- **Date range** — preset (e.g. **This month**) plus **Date from** / **Date to** for custom windows.  
- **Apply** — runs the filter (**do not** embed tenant date literals from screenshots in this catalog).

#### 12.15.2 Results grid

- **Chrome:** **Show *n* entries**; **Search** over the current result set.  
- **Columns:** **Timestamp**; **Transaction type** (examples in capture: **Log in** / **Log out**; **Bank payment**; **Sales receipt**; **Sale invoice**; **Bill payment**—not an exhaustive product list); **Transaction ID** (numeric document reference when applicable—often **blank** for pure session events); **Status** (e.g. **Approved** on postings); **Details** (short human-readable summary such as *Logged in*, *… added*); **User** (display name of actor); **Action** — **View** link (deep-link or detail pane for the underlying transaction—confirm behavior).  
- **Pagination** and “Showing *x* to *y* of *z* entries” footer.

#### 12.15.3 Parity / compliance notes

- Retention period, **export** (if any), and whether **View** respects **role** restrictions are **not** captured here—verify in your tenant and regulatory context.

---

## 13. Typical end-to-end business flows (narrative)

### 13.1 Sell stock from quote to cash

1. Create **customer** (or use existing).  
2. Optional: create **quotation**.  
3. Create **sales order** → approve → **deliver** (delivery note optional) → **invoice** (auto or manual).  
4. Issue **sales invoice** with correct **template** (inline vs distribution), taxes, charges, deductions, project/location tags as needed.  
5. **Email** invoice; attach files if required.  
6. Record **sales receipt**; **allocate** to invoice (manual or FIFO assist); handle **withholding** if applicable. *(Where the business uses **post-dated cheques**, register/clear via **Post Dated Cheque Received** per §5.7.)*  
7. **Print** receipt (optionally two copies).  
8. Review **customer ledger** and **AR reports**.

### 13.2 Buy stock into warehouse

1. Create **supplier**.  
2. Create **purchase order** → approve → receive/bill → **supplier bill** (auto or manual, multi-PO allowed).  
3. Use **batch/expiry** capture on purchase if applicable.  
4. Record **supplier payment** with allocations and withholding as applicable. *(If using **post-dated cheques** to suppliers, use **Post Dated Cheque Issued** — §6.1.)*  
5. Optionally run **landed cost** allocation to true-up inventory value.  
6. Use **stock transfer**/**adjustment** for physical corrections.

### 13.3 Manufacture finished goods

1. Define **assembly template** (standard costs/BOM-like baseline).  
2. Start **assembly job**, issue components, accumulate overheads.  
3. **Finish / approve** job to capitalize finished goods and costs.  
4. Review **assembly reports** for job cost outcomes.

### 13.4 Month-end control

1. Ensure **bank reconciliation** complete.  
2. Run **FX revaluation** if multi-currency.  
3. Post **journals** for accruals/adjustments.  
4. Set/update **lock date** (global and per-user policy).  
5. Run **tax reports** and **management reports**; export to Excel.

### 13.5 Regulated digital sales (where licensed)

1. Complete **digital invoicing setup** per guided materials.  
2. Issue invoices and perform **FBR/PRAL** submission steps as described in digital invoicing tutorials.

### 13.6 Fixed asset lifecycle (when module enabled)

1. Register assets (including bulk **import** where used).  
2. Maintain **valuation / lifecycle** data through the year.  
3. Use **reports and exports** to reconcile asset register to GL where the product provides those links (confirm exact report names in live app).

---

## 14. Transaction dictionary (publicly named abbreviations)

These codes appear in tax/printing announcements:

- **SI** — sales invoice  
- **SC** — sales credit  
- **SO** — sales order  
- **SR** — sales receipt  
- **VI** — supplier purchase invoice (bill) naming in announcements  
- **VC** — **supplier / purchase credit** (Settings → Purchases Printing; aligns with supplier bill **VI**)  
- **PO** — purchase order  
- **SQ** — **sales quotation** (product-description / doc-type grid in Smart Settings)  
- **QO** — **quotation / quote-order** document family in the Smart Settings **Last rate** matrix (listed beside **PO**, **SI**, etc.; confirm exact label in app).  
- **GDNSI / GDNSO** — goods delivery note from invoice / from order  
- **PDCR** — post-dated cheque **received** (sales / customer side; Settings → Sales Printing)  
- **PDCI** — post-dated cheque **issued** (purchases / supplier side; Settings → Purchases Printing)  
- **VP** — supplier **bill payment** (voucher printing)  
- **GRNPO / GRNVI** — **goods receipt note** linked to **purchase order** vs **supplier bill (VI)**  
- **CUS** — **customer** master / listing print template  

**Business Information screen (§12.13) — common PK-style registration labels:** **CNIC** (national ID-style field on business profile); **STN** (sales tax number); **NTN** (national tax number)—exact legal meaning follows your jurisdiction and tenant setup.

**Bank voucher types (API / integration docs):** **EP** — bank payment; **IR** — bank receipt (enumerations used in developer documentation for direct bank movements).

---

## 15. Gaps to close for pixel-perfect parity

Use this checklist when auditing the live system (including your logged-in **administrator** area):

- [ ] Export the **full sidebar/menu** (screenshots or structured export) for **every role** (admin vs restricted vs assembly-only, etc.).  
- [ ] For **each** menu leaf: capture **list columns**, **filters**, **action menu**, **form tabs**, **validation rules**, **print layouts**.  
- [ ] Enumerate **every report name** and its filter panel (public docs quote totals but not exhaustive names).  
- [ ] Record **approval** matrix: which document types support draft/approve.  
- [ ] Record **integration** toggles visible in UI (digital invoicing, SMS credits, API keys).  
- [ ] Capture **subscription** gates (which modules require upgrades, for example multi-location note referencing contacting support).
- [ ] **Fixed assets:** every register screen, depreciation method fields (if any), disposal flow, and GL linkage as implemented in your build.
- [ ] **Online payments:** PayPro/Kuickpay (or successor) configuration screens, settlement reconciliation, and failure/retry UX.
- [ ] **Emails add-on:** trigger catalog, template variables, and throttling/bounce handling if exposed.
- [ ] **Global chrome:** remaining items not listed in **§2.3** / **§12.1** (e.g. notifications, footer links, admin-only controls).
- [ ] **Bank → Revaluation / multi-currency:** exact navigation path if not a sidebar leaf (see §2.1 footnote).
- [ ] **Quotations:** exact entry (Orders vs Sales All vs FAB).
- [ ] **Reports:** expand **every** category and list **all child report names + IDs**. *Partially done in this doc:* **Sales → Sales and Customer** (§10.11.2), **Inventory → Products** (§10.11.3), **Favorites** sample (§10.11.1), **Taxes** subfolders (§10.10.5), **Purchases** subfolders (§10.10.3). *Still needed:* **Sales** other leaves, **Purchases** each leaf, **Bank**, **Financial**, **Assembly**, **Projects**, **Budget**, **Fixed Assets**, **Consolidation**, **Inventory → Letter of Credit**, and **Analytical** categories beyond prior samples.
- [ ] **Assembly operations:** screens for **templates** and **jobs** distinct from **Assembly reports** folder.
- [ ] **Post-dated cheques:** full lifecycle (register PDC → clear on presentation → link to receipt/payment or reversal).
- [ ] **Journals (§9.2.1):** **Add new** / **edit** line-level form (debit–credit grid, projects, attachments); posting and **approval** rules; full **Action** dropdown; **export** row scope; **bulk delete** constraints.
- [ ] **Chart of account / nominals (§9.1):** **Section listing** (§9.1.4) **Edit** / **bulk delete** / **Up–Down** scope; **Section new** validation vs existing nominals; **Nominals** link target vs **Chart of Account** (§9.1.3); **Edit nominal** full **Action** menu; chart **import** or **reorder** if any.
- [ ] **§2.6 vs §2.1 diff:** every item that appears in the **tutorial map** but not in your sidebar (Stock Transfer, Landed Cost, LC, Multi Unit, Batch & Expiry, Bank Revaluation, Multi Currency, Assembly Jobs/Templates, etc.)—confirm **license**, **Settings** toggle, or **hidden menu**.
- [ ] **Sales / purchase credits:** screen entry points (tabs on invoice list vs separate menu).
- [ ] **Smart Settings:** any **collapsed** accordion not fully expanded in §12.2 screenshots—confirm every field default, validation, and dependency (especially **fine** / **PIN** / **bulk code update** warnings).
- [ ] **Taxes and Year End (§12.12):** exact **ADT vs AST** section title in your build; whether **global** vs **section** Save boundaries match user expectations; dependencies when a **tax region** is deleted while **rate rows** still reference it.
- [ ] **Dashboard Management** (Settings): which widgets, ordering, and role visibility rules apply.
- [ ] **OP Methods:** screen purpose and every option (Settings link — §12.1).
- [ ] **Business Information (§12.13):** validation on **CNIC/STN/NTN** formats; logo **MIME** types and **crop** behavior; whether **Apply on all prints** overrides per-template headers from **Printing** settings.
- [ ] **Content Settings (§12.14):** full trees under **Forms** and **Menu**; drill-down for **Project / Bank / Purchase** listing cards or editors; diff vs **Column Management** (same Settings column).
- [ ] **Filters Management** and **Column Management** (Settings — §12.1): full field layout; overlap with **Content Settings** (§12.14) and **list** behavior (**§3.10**).
- [ ] **Email Settings** and **Sent Emails** (Settings — §12.1): screens, template variables, throttling (**§3.6** / **§3.19**).
- [ ] **Lock Date** (§9.5, §12.1): per-user vs global UI if not already covered in tenant capture.
- [ ] **Users / roles (§12.3–§12.4):** **Roles** list / edit / delete flows (not only **Add role**); fully **expanded** **Select rights** trees with exact permission verbs per submodule; where **role** is assigned on **Add user** vs **Edit user**; complete **Action** dropdown on the **Users** table.
- [ ] **User log (§12.15):** full **Type** dropdown values; **View** navigation target; export / API access; retention and **PII** handling if regulated.
- [ ] **Authorisation** (§12.6) and **Advance users** (§12.5): configuration and runtime **approval** / **data-visibility** screens when the add-ons are licensed.

---

## 16. Source map (for maintainers of this catalog)

Primary public bundles:

- Support category browser and articles index: `https://fastaccounts.io/support/`  
- Tutorial navigation (Bank/Sales/Purchases/Inventory/Reports/Assembly/Settings/Others): `https://fastaccounts.io/getting-started-with-fast-accounts/`  
- Feature marketing summaries: `https://fastaccounts.io/feature/`  
- Digital invoicing program description: `https://fastaccounts.io/digital-invoicing-fbr/`  
- Roles and user management deep dive: `https://fastaccounts.io/roles-management-and-user-rights/`  
- Developer API onboarding (confirms **roles**, **API users**, **OTP keys**, token authorization pattern): `https://developer.fastaccounts.io/`
- Homepage / packages / add-on matrix (modules not always listed in support sidebar): `https://fastaccounts.io/`
- Sales module detail page (import, partial order flows, print column control): `https://fastaccounts.io/features/sales/`
- Plans & pricing (tier limits, optional modules): `https://fastaccounts.io/plans-pricing/` (URL as linked from public navigation; verify live site if it moves)

### 16.1 Live UI routes indexed in this catalog (end-to-end map)

Use this table to find **field-level** or **screen-structure** write-ups without scanning every chapter. Rows cover **Settings / GL**, **reporting hubs**, **sidebar operational areas**, and **assembly**. **§1** (access, subscription, **API users**, commercial surfaces) is **not** a single in-app breadcrumb—see that chapter for product entry context. **§2** documents **global navigation** (live sidebar **§2.1**, support/marketing taxonomy **§2.2**, header/chrome **§2.3**, assembly entry note **§2.4**, general journal Settings entry **§2.5** → journals list **§9.2.1**, tutorial cross-check **§2.6**) and complements the table rows below. **§14** is the **abbreviation / doc-code dictionary**, not a live route. **§13** is **narrative end-to-end flows** (no single URL). Anything else **not** listed in the table is either **narrative-only** elsewhere (deeper **§4–§8** leaf screens, full **§10** report enumeration) or still **gap-listed** (**§15**).

| Live route / screen (breadcrumb or title) | Primary section(s) |
|---------------------------------------------|-------------------|
| **Home / Journals** | **§9.2.1** |
| **Home / Chart of Account**; **Nominal Account New** modal | **§9.1.1**, **§9.1.2** |
| **Home / Section Listing**; **Section New** modal | **§9.1.4** |
| **Nominals** (separate menu item — parity) | **§9.1.3** |
| **Home / Smart Settings** | **§12.2** (§12.2.1–§12.2.9) |
| **Home / Taxes and Year End** | **§12.12** |
| **Home / Business information** | **§12.13** |
| **Home / Content Settings** (incl. Listing → Sales / Inventory etc.) | **§12.14** |
| **Home / Users**; **Add User** | **§12.3** |
| **Home / Roles**; **Add Role** | **§12.4** |
| **Home / User Log** | **§12.15** |
| **Dashboard** (home widgets) | **§10.9** |
| **Reports** hub (standard reports tree + cards) | **§10.10** (**§10.10.1**–**§10.10.5**); partial leaf lists **§10.11** |
| **Analytical Reports** hub | **§10.3** (layout); runner UX **§10.12** |
| **Switch company** / session rail (not a “page”) | **§2.3**; **§12.1** right rail |
| **Bank**, **Sales**, **Purchases**, **Inventory** (main sidebar areas) | Sidebar map **§2.1**; feature narratives **§4**–**§7** |
| **Fixed assets** (optional module) | **§8**; reports **§10** where named |
| **Assembly** (manufacturing / kitting) | Concepts **§11**; reports under **§10** / **§10.10** when enabled |

**Settings mega-menu links in §12.1 not expanded field-by-field in this file:** **Lock Date** (policy — **§9.5**); **OP Methods**; **Dashboard Management** (widget model — **§10.9**); **Filters Management**; **Column Management**; **Missed Recurrence** (**§3.3**); **Email Settings**; **Sent Emails** (**§3.6** / **§3.19**); **Budget** and **Authorisation** as named product areas (**§9.3**, **§12.6**); **Location** (**§12.7**); **Printing** matrix (**§12.1** printing table + **§12.8**); **Advance users** premium fence (**§12.5**) and support label (**§12.9**). **§12.10** and **§12.11** are **support / legal** topic labels in this catalog, not live **Settings** screen walkthroughs. **API keys / developer access** are summarized under product entry (**§1.4**) and URLs in **§16**, not as a field-level Settings screen in this catalog. Treat **§15** as the authoritative “still to capture” list.

**In-app screenshots (this repo):** sidebar, **Reports** hub, **Settings** mega-menu / header chrome, **Smart Settings** accordion pages, **Taxes and Year End** (§12.12), **Business Information** (§12.13), **Content Settings** (§12.14), **Users** / **Add user** / **Add role** (§12.3–§12.4), **User log** (§12.15), **Journals** list (§9.2.1), **Chart of Account** / nominal modal (§9.1), **Section listing** / **Section new** (§9.1.4), and Analytical Reports captures live under the workspace `assets/` folder from Cursor image uploads—use those for UI parity while keeping **PINs, serial numbers, prefixes, tax rates, tax codes, COA numbers, nominal and section codes and names, addresses, phones, emails, subscription account IDs, renewal dates, financial values, party names, log timestamps tied to real events, transaction IDs, and journal totals** out of versioned docs.

---

*End of catalog.*
