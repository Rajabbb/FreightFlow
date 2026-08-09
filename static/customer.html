<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Müştəri Paneli - LogiFast</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-blue: #4f46e5;
            --primary-hover: #4338ca;
            --secondary-color: #0ea5e9;
            --bg-gradient: linear-gradient(145deg, #f0f4f8 0%, #e2e8f0 100%);
            --card-bg: rgba(255, 255, 255, 0.85);
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: rgba(226, 232, 240, 0.8);
            --radius-lg: 20px;
            --radius-md: 12px;
            --radius-sm: 8px;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-gradient);
            color: var(--text-main);
            font-size: 14px;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
            overflow-x: hidden;
        }

        ::-webkit-scrollbar { width: 7px; height: 7px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; border: 2px solid #f0f4f8; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

        .navbar {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
            position: sticky;
            top: 0;
            z-index: 1020;
        }

        .navbar-brand {
            background: linear-gradient(45deg, var(--primary-blue), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.15rem;
        }

        .card {
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: var(--radius-lg);
            box-shadow: 0 15px 35px -15px rgba(15, 23, 42, 0.05);
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 24px;
            margin-bottom: 24px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            width: 100%;
            word-break: break-word;
        }

        .section-title {
            font-size: 17px;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.02em;
            flex-wrap: wrap;
        }

        .section-title i {
            font-size: 20px;
            background: linear-gradient(135deg, #4f46e5 0%, #0ea5e9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .section-desc {
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 20px;
            font-weight: 500;
        }

        .form-control, .form-select {
            padding: 10px 14px;
            border-radius: var(--radius-md);
            border: 1px solid #e2e8f0;
            font-size: 13.5px;
            background-color: #f8fafc;
            color: var(--text-main);
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.01);
            width: 100%;
        }

        .form-control:focus, .form-select:focus {
            background-color: #ffffff;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12), inset 0 1px 2px rgba(0, 0, 0, 0.02);
            outline: none;
            transform: translateY(-1px);
        }

        .form-control::placeholder { color: #94a3b8; }

        .form-label {
            font-size: 12.5px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 6px;
            letter-spacing: -0.01em;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary-blue) 0%, #3b82f6 100%);
            border: none;
            padding: 11px 20px;
            border-radius: var(--radius-md);
            font-weight: 700;
            font-size: 13.5px;
            letter-spacing: 0.3px;
            color: white;
            box-shadow: 0 8px 16px -8px rgba(79, 70, 229, 0.5), inset 0 1px 0 rgba(255,255,255,0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            width: 100%;
        }

        .btn-primary:hover {
            background: linear-gradient(135deg, var(--primary-hover) 0%, #2563eb 100%);
            transform: translateY(-2px);
            box-shadow: 0 12px 20px -8px rgba(79, 70, 229, 0.6), inset 0 1px 0 rgba(255,255,255,0.2);
            color: white;
        }

        .stats-card {
            border-radius: var(--radius-lg);
            padding: 20px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255,255,255,1);
            box-shadow: 0 12px 25px -10px rgba(0, 0, 0, 0.04);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            height: 100%;
        }

        .stats-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 5px; height: 100%;
            background: linear-gradient(to bottom, var(--primary-blue), #8b5cf6);
            border-radius: 10px 0 0 10px;
        }

        .stats-card:nth-child(2)::before { background: linear-gradient(to bottom, #10b981, #34d399); }
        .stats-card:nth-child(3)::before { background: linear-gradient(to bottom, #f59e0b, #fbbf24); }

        .stats-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 16px 30px -10px rgba(0, 0, 0, 0.08);
        }

        .stats-card h3 {
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 6px;
            margin-bottom: 0;
        }

        .optional-box {
            background: rgba(248, 250, 252, 0.6);
            border: 2px dashed #cbd5e1;
            border-radius: var(--radius-lg);
            padding: 18px;
            margin-top: 20px;
            transition: border-color 0.3s;
        }

        .opt-row {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: var(--radius-md);
            padding: 12px 14px;
            margin-bottom: 10px;
            box-shadow: 0 3px 5px -3px rgba(0, 0, 0, 0.02);
            transition: all 0.2s ease;
        }

        .form-check-input {
            width: 1.15em;
            height: 1.15em;
            border: 2px solid #cbd5e1;
            transition: all 0.2s ease;
            cursor: pointer;
            flex-shrink: 0;
        }
        
        .form-check-input:checked {
            background-color: var(--primary-blue);
            border-color: var(--primary-blue);
            box-shadow: 0 0 8px rgba(79, 70, 229, 0.3);
        }

        .form-check-label {
            cursor: pointer;
            font-size: 13.5px;
        }

        .carrier-select-box {
            max-height: 220px;
            overflow-y: auto;
            border: 1px solid #e2e8f0;
            border-radius: var(--radius-md);
            padding: 8px;
            background: #ffffff;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.01);
        }

        .carrier-item-row {
            display: flex;
            align-items: center;
            padding: 8px 10px;
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
            cursor: pointer;
            border: 1px solid transparent;
            margin-bottom: 3px;
        }

        .carrier-item-row:hover {
            background: #f8fafc;
            border-color: #e2e8f0;
        }

        .request-card {
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: var(--radius-lg);
            padding: 20px;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .request-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
            background: linear-gradient(to bottom, var(--primary-blue), var(--secondary-color));
        }

        .request-meta-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: var(--radius-md);
            padding: 12px 14px;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.01);
        }

        .modal-content {
            border: none;
            border-radius: var(--radius-lg);
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        .modal-header {
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            padding: 18px 22px;
        }
        
        .modal-body { padding: 22px; }
        
        .modal-footer {
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            padding: 14px 22px;
        }

        .badge {
            padding: 5px 10px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.3px;
        }

        .table-container-responsive {
            width: 100%;
            min-width: 0;
            flex: 1 1 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-top: 12px;
            padding-bottom: 8px;
            display: block;
            touch-action: pan-x;
        }

        .table-container-responsive table {
            min-width: 650px;
            width: 100%;
            white-space: nowrap;
        }

        img, svg { max-width: 100%; height: auto; }

        .table-container-responsive.overflow-hidden {
            overflow-x: auto !important;
            overflow-y: hidden !important;
        }

        @media (max-width: 768px) {
            .container-fluid { padding-left: 12px; padding-right: 12px; }
            .stats-card h3 { font-size: 28px; }
            .section-title { font-size: 16px; }
        }

        @media (max-width: 576px) {
            .card { padding: 16px; }
            .optional-box { padding: 12px; }
            .stats-card { padding: 16px; }
            .stats-card h3 { font-size: 24px; }
            .navbar-brand { font-size: 1rem; }
            body { font-size: 13.5px; }
            .section-title { font-size: 15px; }
            .section-desc { font-size: 12.5px; }
            .modal-body { padding: 16px; }
            .modal-header { padding: 14px 16px; }
            .modal-footer { padding: 12px 16px; }
            .btn { white-space: normal; }
            #userCompanyName { max-width: 100px; }
        }

        @media (max-width: 400px) {
            .navbar-brand { font-size: 0.9rem; }
            .navbar-brand i { font-size: 0.95rem; }
            #userCompanyName { max-width: 76px; font-size: 11.5px; padding-left: 8px !important; padding-right: 8px !important; }
            .stats-card h3 { font-size: 21px; }
            .section-title { font-size: 14px; flex-wrap: wrap; }
            .section-title i { font-size: 17px; }
            .card { padding: 12px; }
            .request-card { padding: 14px; }
            .badge { font-size: 10px; padding: 4px 8px; }
            body { font-size: 13px; }
        }

        @media (max-width: 340px) {
            #userCompanyName { display: none; }
        }

        /* ============ RFQ DETAIL PAGE ============ */
        .detail-header-card {
            border-radius: var(--radius-lg);
            padding: 20px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255,255,255,1);
            box-shadow: 0 12px 25px -10px rgba(0, 0, 0, 0.04);
        }

        .mini-stat-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 10px;
        }

        @media (max-width: 700px) {
            .mini-stat-grid {
                grid-auto-flow: column;
                grid-auto-columns: minmax(96px, 1fr);
                grid-template-columns: none;
                overflow-x: auto;
                padding-bottom: 4px;
                -webkit-overflow-scrolling: touch;
            }
        }

        .mini-stat-box {
            border: 1px solid #e2e8f0;
            border-radius: var(--radius-md);
            background: #f8fafc;
            padding: 12px 10px;
            text-align: center;
        }

        .mini-stat-box .mini-stat-icon {
            width: 30px; height: 30px;
            border-radius: 9px;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 14px;
            margin-bottom: 6px;
        }

        .mini-stat-box .mini-stat-value { font-size: 20px; font-weight: 800; color: var(--text-main); line-height: 1; }
        .mini-stat-box .mini-stat-label { font-size: 10.5px; color: var(--text-muted); font-weight: 700; margin-top: 3px; display: block; }

        .avatar-circle {
            width: 38px; height: 38px; min-width: 38px;
            border-radius: 50%;
            display: inline-flex; align-items: center; justify-content: center;
            font-weight: 800; font-size: 13px; color: #fff;
        }

        .carrier-panel-row {
            border: 1px solid #e2e8f0;
            border-radius: var(--radius-md);
            padding: 10px 12px;
            margin-bottom: 8px;
            background: #fff;
            transition: all 0.2s ease;
        }
        .carrier-panel-row:hover { border-color: #c7d2fe; background: #f8fafc; }

        .filter-pill {
            border: 1px solid #e2e8f0;
            background: #fff;
            border-radius: 30px;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 700;
            color: var(--text-muted);
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .filter-pill.active {
            background: var(--primary-blue);
            border-color: var(--primary-blue);
            color: #fff;
        }

        #carriersPanel {
            width: 100%;
            max-width: 400px;
        }

        .envelope-box {
            width: 100%;
            min-height: 120px;
            border-radius: var(--radius-lg);
            background: linear-gradient(135deg, #eef2ff 0%, #e0f2fe 100%);
            display: flex; align-items: center; justify-content: center;
        }
    </style>
</head>
<body>

    <!-- NAVBAR -->
    <nav class="navbar navbar-expand-lg navbar-light py-2">
        <div class="container-fluid px-3 px-md-4">
            <a class="navbar-brand fw-bold text-truncate d-flex align-items-center" href="#">
                <i class="bi bi-lightning-charge-fill me-1" style="color: var(--primary-blue);"></i> LogiFast 
                <span class="text-muted fs-6 fw-normal ms-1 d-none d-sm-inline" style="color: #64748b !important;">| Müştəri Paneli</span>
            </a>
            <div class="ms-auto d-flex align-items-center gap-2">
                <span id="userCompanyName" class="fw-bold text-dark small px-2 px-md-3 py-1.5 rounded-pill text-truncate" style="background: #f1f5f9; max-width: 130px;">Şirkət</span>
                <button onclick="logout()" class="btn btn-outline-danger btn-sm px-2.5 py-1.5 rounded-pill text-nowrap" style="font-size: 12.5px;">
                    <i class="bi bi-box-arrow-right me-1"></i> Çıxış
                </button>
            </div>
        </div>
    </nav>

    <div class="container-fluid px-2 px-sm-3 px-md-4 py-3 py-md-4" id="dashboardMain">
        
        <!-- STATS ROW -->
        <div class="row g-2 g-md-3 mb-4">
            <div class="col-12 col-sm-4">
                <div class="stats-card">
                    <span class="text-muted small fw-bold text-uppercase tracking-wider">Aktiv RFQ Sorğuları</span>
                    <h3 id="statActiveRfqs">0</h3>
                </div>
            </div>
            <div class="col-12 col-sm-4">
                <div class="stats-card">
                    <span class="text-muted small fw-bold text-uppercase tracking-wider">Tamamlanmış Daşımalar</span>
                    <h3 id="statCompleted">0</h3>
                </div>
            </div>
            <div class="col-12 col-sm-4">
                <div class="stats-card">
                    <span class="text-muted small fw-bold text-uppercase tracking-wider">Daşıyıcı Bazası</span>
                    <h3 id="statCarriersCount">0</h3>
                </div>
            </div>
        </div>

        <!-- DAŞIYICI BAZASINI İDARƏ ETMƏK -->
        <div class="card shadow-sm border-0 mb-4">
            <div class="section-title mb-1">
                <i class="bi bi-people-fill text-primary"></i> Daşıyıcı Bazasını İdarə Etmək
            </div>
            <div class="section-desc mb-3">Daşıyıcıları istədiyiniz üsulla bazaya əlavə edin və ya idarə edin.</div>

            <ul class="nav nav-pills mb-3 gap-2 flex-column flex-sm-row" id="carrierTabs" role="tablist">
                <li class="nav-item flex-fill text-center" role="presentation">
                    <button class="nav-link active px-3 py-2 fw-semibold w-100" id="file-tab" data-bs-toggle="pill" data-bs-target="#file-content" type="button" role="tab" style="font-size: 13px;">
                        <i class="bi bi-file-earmark-excel me-1"></i> Fayl Yüklə
                    </button>
                </li>
                <li class="nav-item flex-fill text-center" role="presentation">
                    <button class="nav-link px-3 py-2 fw-semibold w-100" id="manual-tab" data-bs-toggle="pill" data-bs-target="#manual-content" type="button" role="tab" style="font-size: 13px;">
                        <i class="bi bi-person-plus me-1"></i> Əllə Daxil Et
                    </button>
                </li>
                <li class="nav-item flex-fill text-center" role="presentation">
                    <button class="nav-link px-3 py-2 fw-semibold w-100" id="paste-tab" data-bs-toggle="pill" data-bs-target="#paste-content" type="button" role="tab" style="font-size: 13px;">
                        <i class="bi bi-clipboard-text me-1"></i> Cədvəldən Yapışdır
                    </button>
                </li>
            </ul>

            <div class="tab-content mb-3" id="carrierTabsContent">
                
                <div class="tab-pane fade show active" id="file-content" role="tabpanel">
                    <form onsubmit="uploadCarriers(event)" class="p-3 border rounded bg-light">
                        <div class="row align-items-end g-3">
                            <div class="col-12 col-md-8">
                                <label class="form-label text-muted">Excel / CSV Faylı Yüklə</label>
                                <input type="file" class="form-control" name="file" accept=".csv, .xlsx, .xls" required>
                            </div>
                            <div class="col-12 col-md-4">
                                <button type="submit" class="btn btn-primary w-100">
                                    <i class="bi bi-cloud-arrow-up-fill me-2"></i> Əlavə Et
                                </button>
                            </div>
                        </div>
                    </form>
                </div>

                <div class="tab-pane fade" id="manual-content" role="tabpanel">
                    <form onsubmit="addManualCarrier(event)" class="p-3 border rounded bg-light">
                        <div class="mb-3">
                            <label class="form-label text-muted">Şirkət / Daşıyıcı Adı</label>
                            <input type="text" class="form-control" id="manual_company_name" placeholder="Məsələn: LogiTrans MMC" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-muted">E-poçt Ünvanı</label>
                            <input type="email" class="form-control" id="manual_email" placeholder="info@logitrans.az" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                            <i class="bi bi-person-plus-fill me-2"></i> Daşıyıcıyı Əlavə Et
                        </button>
                    </form>
                </div>

                <div class="tab-pane fade" id="paste-content" role="tabpanel">
                    <form onsubmit="addPasteCarrier(event)" class="p-3 border rounded bg-light">
                        <div class="mb-3">
                            <label class="form-label text-muted">Excel-dən sütunları kopyalayıb bura yapışdırın:</label>
                            <textarea class="form-control" id="paste_raw_text" rows="3" placeholder="Şirkət A&#10;a@example.com&#10;Şirkət B&#10;b@example.com" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary w-100" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                            <i class="bi bi-file-earmark-text-fill me-2"></i> Cədvəldən Əlavə Et
                        </button>
                    </form>
                </div>

            </div>

            <hr class="my-3 text-muted opacity-25">

            <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
                <span class="fw-bold text-dark small text-uppercase tracking-wider">
                    <i class="bi bi-list-ul text-primary me-1"></i> Bazadakı Mövcud Daşıyıcılar
                </span>
                <div class="d-flex align-items-center gap-2">
                    <!-- YENİLİK: Daşıyıcı Axtarış Sətri -->
                    <input type="text" id="carrierSearchInput" class="form-control form-control-sm" placeholder="Daşıyıcı axtar..." onkeyup="filterManageCarriers()" style="width: 160px; font-size: 12px;">
                    <button type="button" class="btn btn-sm btn-outline-secondary rounded-pill px-3 py-1" onclick="loadManageCarriersList()" style="font-size: 11px;">
                        <i class="bi bi-arrow-clockwise me-1"></i> Yenilə
                    </button>
                </div>
            </div>
            <div class="carrier-select-box" id="manageCarriersContainer">
                <span class="text-muted small">Daşıyıcılar yüklənir...</span>
            </div>
        </div>

        <!-- YENİ YÜK SORĞUSU (RFQ) YARAT -->
        <div class="card">
            <div class="section-title">
                <i class="bi bi-box-seam-fill"></i> Yeni Yük Sorğusu (RFQ) Yarat
            </div>
            <div class="section-desc">Logistika parametrlərini ətraflı daxil edin və sorğunuzu göndərin.</div>
            
            <form id="rfqForm" onsubmit="createRfq(event)">
                <div class="row g-2 g-md-3 mb-2">
                    <div class="col-12 col-md-6">
                        <label class="form-label">Loading Location (Yükləmə yeri) <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="origin" required placeholder="məs: Bakı, Azərbaycan">
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Delivery Location (Boşaltma yeri) <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="destination" required placeholder="məs: İstanbul, Türkiyə">
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Cargo Type (Yükün növü) <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="cargo_type" required placeholder="məs: Quru yük / Tekstil">
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Weight (Çəki - kq) <span class="text-danger">*</span></label>
                        <input type="number" step="any" class="form-control" id="weight_kg" required placeholder="1000">
                    </div>
                    <div class="col-12">
                        <label class="form-label">Transportation Mode (Daşınma Növü) <span class="text-danger">*</span></label>
                        <select class="form-select" id="transportation_mode" required>
                            <option value="">Daşınma növünü seçin...</option>
                            <option value="Quru (Road)">Quru (Road)</option>
                            <option value="Hava (Air)">Hava (Air)</option>
                            <option value="Su/Dəniz (Sea)">Su / Dəniz (Sea)</option>
                            <option value="Dəmiryolu (Rail)">Dəmiryolu (Rail)</option>
                        </select>
                    </div>
                </div>

                <div class="optional-box">
                    <label class="form-label fw-bold mb-3 text-dark fs-6 d-flex align-items-center">
                        <i class="bi bi-sliders text-primary me-2 fs-5"></i> İxtiyari (Optional) Parametrlər
                    </label>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_loading_date" onchange="toggleOptField('loading_date')">
                            <label class="form-check-label fw-bold text-dark" for="chk_loading_date">Loading Date (Yükləmə tarixi)</label>
                        </div>
                        <input type="date" class="form-control opt-input d-none mt-2" id="inp_loading_date">
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_truck_type" onchange="toggleOptField('truck_type')">
                            <label class="form-check-label fw-bold text-dark" for="chk_truck_type">Truck Type (Maşın növü)</label>
                        </div>
                        <input type="text" class="form-control opt-input d-none mt-2" id="inp_truck_type" placeholder="məs: Tentli / Refrijerator">
                    </div>
                    
                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_volume" onchange="toggleOptField('volume')">
                            <label class="form-check-label fw-bold text-dark" for="chk_volume">Volume (CBM)</label>
                        </div>
                        <input type="text" class="form-control opt-input d-none mt-2" id="inp_volume" placeholder="məs: 15 m3">
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_hs_code" onchange="toggleOptField('hs_code')">
                            <label class="form-check-label fw-bold text-dark" for="chk_hs_code">HS Code</label>
                        </div>
                        <input type="text" class="form-control opt-input d-none mt-2" id="inp_hs_code" placeholder="məs: 1234.56">
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_stackable" onchange="toggleOptField('stackable')">
                            <label class="form-check-label fw-bold text-dark" for="chk_stackable">Stackable / Non-stackable</label>
                        </div>
                        <select class="form-select opt-input d-none mt-2" id="inp_stackable">
                            <option value="">Seçin...</option>
                            <option value="Stackable">Stackable</option>
                            <option value="Non-stackable">Non-stackable</option>
                        </select>
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_shipment_type" onchange="toggleOptField('shipment_type')">
                            <label class="form-check-label fw-bold text-dark" for="chk_shipment_type">Shipment Type (FTL / LTL / LCL / FCL)</label>
                        </div>
                        <input type="text" class="form-control opt-input d-none mt-2" id="inp_shipment_type" placeholder="məs: FTL">
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_incoterm" onchange="toggleOptField('incoterm')">
                            <label class="form-check-label fw-bold text-dark" for="chk_incoterm">Incoterm</label>
                        </div>
                        <input type="text" class="form-control opt-input d-none mt-2" id="inp_incoterm" placeholder="məs: EXW / FAP">
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_adr" onchange="toggleOptField('adr')">
                            <label class="form-check-label fw-bold text-dark" for="chk_adr">Dangerous Goods (ADR)</label>
                        </div>
                        <input type="text" class="form-control opt-input d-none mt-2" id="inp_adr" placeholder="məs: Klass 3">
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_temp" onchange="toggleOptField('temp')">
                            <label class="form-check-label fw-bold text-dark" for="chk_temp">Temperature Requirement (Reefer)</label>
                        </div>
                        <input type="text" class="form-control opt-input d-none mt-2" id="inp_temp" placeholder="məs: +2 to +8 °C">
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_deliv_date" onchange="toggleOptField('deliv_date')">
                            <label class="form-check-label fw-bold text-dark" for="chk_deliv_date">Delivery Deadline</label>
                        </div>
                        <input type="date" class="form-control opt-input d-none mt-2" id="inp_deliv_date">
                    </div>

                    <div class="opt-row">
                        <div class="form-check mb-1">
                            <input class="form-check-input opt-check" type="checkbox" id="chk_info" onchange="toggleOptField('info')">
                            <label class="form-check-label fw-bold text-dark" for="chk_info">Additional Information (Qeyd və ya sənəd əlavəsi)</label>
                        </div>
                        <div id="inp_info_container" class="d-none mt-2">
                            <textarea class="form-control mb-2" id="inp_info_text" rows="2" placeholder="Əlavə xüsusi şərtlər və təlimatlar..."></textarea>
                            <label class="form-label text-muted small mb-1">Əlavə fayl yüklə (istəyə bağlı):</label>
                            <input type="file" class="form-control" id="inp_info_file">
                        </div>
                    </div>
                </div>

                <div class="p-3 mt-3 mb-3 bg-white border rounded-4">
                    <label class="form-label fw-bold text-dark fs-6 mb-3 d-flex align-items-center">
                        <i class="bi bi-envelope-paper-fill text-primary me-2 fs-5"></i> Daşıyıcılara Göndəriləcək Email Məzmunu
                    </label>
                    
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="radio" name="emailTemplateOption" id="standardTemplateRadio" checked onchange="toggleEmailTemplateFields()">
                        <label class="form-check-label fw-bold text-dark" for="standardTemplateRadio">
                            Standart Şablon
                        </label>
                    </div>

                    <div class="p-3 mb-3 bg-light border rounded-3 text-muted small shadow-sm overflow-x-auto" style="font-family: monospace; white-space: pre-wrap; font-size: 12px;">Dear {{company_name}},

Please review the shipment details below and kindly complete the quotation form using the link provided.

Thank you.

Best regards,
{{sender_company}}</div>

                    <div class="form-check mb-3">
                        <input class="form-check-input" type="radio" name="emailTemplateOption" id="customTemplateRadio" onchange="toggleEmailTemplateFields()">
                        <label class="form-check-label fw-bold text-dark" for="customTemplateRadio">
                            Öz Şablonumu Daxil Et (Custom)
                        </label>
                    </div>

                    <div id="customEmailContainer" class="d-none mt-2">
                        <textarea class="form-control" id="custom_email_body" rows="3" placeholder="Email mətnini bura yazın..."></textarea>
                    </div>
                </div>

                <div class="p-3 mt-3 mb-3 bg-white border rounded-4">
                    <label class="form-label fw-bold text-dark fs-6 mb-3 d-flex align-items-center">
                        <i class="bi bi-send-check-fill text-primary me-2 fs-5"></i> Daşıyıcı Paylaşım Ayarı
                    </label>
                    
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="radio" name="carrierOption" id="sendToAllRadio" checked onchange="toggleCarrierSelection()">
                        <label class="form-check-label fw-bold text-dark" for="sendToAllRadio">
                            Sorğunu bütün daşıyıcılara göndər
                        </label>
                    </div>

                    <div class="form-check mb-3">
                        <input class="form-check-input" type="radio" name="carrierOption" id="sendToSelectedRadio" onchange="toggleCarrierSelection()">
                        <label class="form-check-label fw-bold text-dark" for="sendToSelectedRadio">
                            Seçilmiş daşıyıcılara göndər
                        </label>
                    </div>

                    <div id="carrierSelectionContainer" class="d-none mt-2 p-2 p-sm-3 bg-light rounded-4 border">
                        <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
                            <small class="text-muted fw-bold text-uppercase tracking-wider" style="font-size: 11px;">Daşıyıcıları seçin:</small>
                            <div>
                                <button type="button" class="btn btn-sm btn-light fw-bold me-1 px-2 py-1" style="font-size: 11.5px;" onclick="selectAllCarriers(true)">Hamısını Seç</button>
                                <button type="button" class="btn btn-sm btn-link text-muted fw-semibold text-decoration-none px-1 py-1" style="font-size: 11.5px;" onclick="selectAllCarriers(false)">Təmizlə</button>
                            </div>
                        </div>
                        <div class="carrier-select-box" id="carrierCheckboxList">
                            <span class="text-muted small">Daşıyıcılar yüklənir...</span>
                        </div>
                    </div>
                </div>

                <div class="mt-3">
                    <button type="submit" class="btn btn-primary btn-lg w-100 py-3" id="submitRfqBtn">
                        <i class="bi bi-rocket-takeoff-fill me-2"></i> RFQ Sorğusunu Yarat və Göndər
                    </button>
                </div>
            </form>
        </div>

        <!-- AKTİV VƏ KEÇMİŞ SORĞULAR -->
        <div class="card">
            <div class="section-title">
                <i class="bi bi-ui-checks-grid"></i> RFQ Sorğuları və Təkliflər
            </div>
            <div class="section-desc">Yaratdığınız sorğuların statusunu izləyin və təklifləri analiz edin.</div>
            
            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                <h5 class="fw-bold mb-0 text-dark small text-uppercase tracking-wider">Sorğu Siyahısı</h5>
                <div class="d-flex align-items-center gap-2">
                    <!-- YENİLİK: Sorğu Axtarış Sətri -->
                    <input type="text" id="requestSearchInput" class="form-control form-control-sm" placeholder="Sorğularda axtar..." onkeyup="filterRequests()" style="width: 180px; font-size: 12px;">
                    <button type="button" class="btn btn-outline-primary btn-sm rounded-pill px-3 d-flex align-items-center gap-1" onclick="loadRequests()" style="font-size: 12px;">
                        <i class="bi bi-arrow-clockwise"></i> Yenilə
                    </button>
                </div>
            </div>

            <div id="requestsContainer" class="mt-2">
                <p class="text-muted small">Sorğular yüklənir...</p>
            </div>
        </div>

    </div>

    <!-- DETALLI BAXIŞ MODALI -->
    <div class="modal fade" id="quoteDetailModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable mx-2 mx-sm-auto">
            <div class="modal-content">
                <div class="modal-header d-flex justify-content-between align-items-center">
                    <h5 class="modal-title fw-bold text-dark mb-0 d-flex align-items-center" style="font-size: 1.05rem;">
                        <i class="bi bi-file-earmark-text-fill text-primary me-2"></i> Təklif Detalları
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="modalQuoteContent"></div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary px-3 py-1.5 fw-semibold rounded-pill w-100 w-sm-auto" style="font-size: 13px;" data-bs-dismiss="modal">Bağla</button>
                </div>
            </div>
        </div>
    </div>

    <!-- =============== RFQ DETAIL SƏHİFƏSİ =============== -->
    <div id="rfqDetailPage" class="container-fluid px-2 px-sm-3 px-md-4 py-3 py-md-4 d-none">

        <div class="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-2">
            <nav style="font-size: 13px;">
                <a href="#" onclick="closeRfqDetail(); return false;" class="text-decoration-none text-primary fw-bold">
                    <i class="bi bi-arrow-left me-1"></i>RFQ-lar
                </a>
                <span class="text-muted mx-1">›</span>
                <span class="text-dark fw-bold" id="detailBreadcrumbId">RFQ #</span>
            </nav>
            <div class="d-flex align-items-center gap-2">
                <button type="button" class="btn btn-sm btn-outline-secondary rounded-pill px-3" onclick="refreshRfqDetail()">
                    <i class="bi bi-arrow-clockwise me-1"></i> Yenilə
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary rounded-pill px-3" data-bs-toggle="offcanvas" data-bs-target="#carriersPanel">
                    <i class="bi bi-people-fill me-1"></i> Daşıyıcılar (<span id="mobileCarriersCount">0</span>)
                </button>
            </div>
        </div>

        <div class="row g-3 g-lg-4">
            <!-- ƏSAS SÜTUN (tam en) -->
            <div class="col-12">

                <!-- RFQ BAŞLIĞI -->
                <div class="detail-header-card mb-3">
                    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center mb-3 gap-2">
                        <div class="d-flex align-items-center flex-wrap gap-2">
                            <span class="badge bg-light text-secondary border shadow-sm" id="detailIdBadge">ID: —</span>
                            <h5 class="fw-bold text-dark mb-0 d-flex align-items-center flex-wrap gap-1" style="font-size: 1.05rem;">
                                <span class="text-break" id="detailOrigin">—</span>
                                <i class="bi bi-arrow-right-short text-primary fs-5"></i>
                                <span class="text-break" id="detailDestination">—</span>
                            </h5>
                        </div>
                        <span class="badge bg-primary shadow-sm" id="detailStatusBadge">OPEN</span>
                    </div>
                    <div class="row text-muted small fw-medium g-2 mb-3">
                        <div class="col-12 col-sm-4"><i class="bi bi-box-seam me-1 text-primary"></i> Növ: <strong class="text-dark" id="detailCargoType">—</strong></div>
                        <div class="col-12 col-sm-4"><i class="bi bi-speedometer2 me-1 text-primary"></i> Çəki: <strong class="text-dark" id="detailWeight">—</strong></div>
                        <div class="col-12 col-sm-4"><i class="bi bi-calendar-event me-1 text-primary"></i> Yükləmə: <strong class="text-dark" id="detailDeadline">—</strong></div>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-primary rounded-pill px-3" style="font-size: 12px;" data-bs-toggle="modal" data-bs-target="#requestExtraModal">
                        <i class="bi bi-info-circle me-1"></i> Daha ətraflı məlumat
                    </button>
                </div>

                <!-- GÖNDƏRİLMƏ STATUSU -->
                <div class="card mb-3">
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <div class="section-title mb-0">
                            <i class="bi bi-graph-up-arrow"></i> Göndərilmə statusu
                        </div>
                        <button type="button" id="checkBouncesBtn" class="btn btn-sm btn-outline-secondary rounded-pill px-2 py-1 d-inline-flex align-items-center gap-1" style="font-size: 11px;" onclick="checkBouncesNow()" title="Gmail qutusunu çatdırılmayan maillər üçün indi yoxla">
                            <i class="bi bi-arrow-repeat"></i> Bounce yoxla
                        </button>
                    </div>
                    <div class="section-desc mb-2">Sorğunun daşıyıcılara çatdırılma və reaksiya statistikası.</div>

                    <div class="mini-stat-grid mb-3">
                        <div class="mini-stat-box">
                            <span class="mini-stat-icon" style="background:#eef2ff; color:#4f46e5;"><i class="bi bi-send-fill"></i></span>
                            <span class="mini-stat-value" id="statSent">0</span>
                            <span class="mini-stat-label">Göndərildi</span>
                        </div>
                        <div class="mini-stat-box">
                            <span class="mini-stat-icon" style="background:#dcfce7; color:#16a34a;"><i class="bi bi-check-circle-fill"></i></span>
                            <span class="mini-stat-value" id="statDelivered">0</span>
                            <span class="mini-stat-label">Çatdırıldı</span>
                        </div>
                        <div class="mini-stat-box">
                            <span class="mini-stat-icon" style="background:#f1f5f9; color:#334155;"><i class="bi bi-eye-fill"></i></span>
                            <span class="mini-stat-value" id="statViewed">0</span>
                            <span class="mini-stat-label">Baxıldı</span>
                        </div>
                        <div class="mini-stat-box">
                            <span class="mini-stat-icon" style="background:#fef9c3; color:#ca8a04;"><i class="bi bi-chat-left-text-fill"></i></span>
                            <span class="mini-stat-value" id="statQuoted">0</span>
                            <span class="mini-stat-label">Təklif alındı</span>
                        </div>
                        <div class="mini-stat-box">
                            <span class="mini-stat-icon" style="background:#fee2e2; color:#dc2626;"><i class="bi bi-exclamation-triangle-fill"></i></span>
                            <span class="mini-stat-value" id="statFailed">0</span>
                            <span class="mini-stat-label">Çatdırılmadı</span>
                        </div>
                    </div>

                    <button type="button" class="btn btn-sm btn-outline-primary rounded-pill px-3 d-inline-flex align-items-center gap-1" style="font-size: 12px;" data-bs-toggle="offcanvas" data-bs-target="#carriersPanel">
                        <i class="bi bi-people-fill"></i> Daşıyıcılar (<span id="statBtnCarriersCount">0</span>)
                    </button>
                </div>

                <!-- TƏKLİFLƏR -->
                <div class="card mb-3">
                    <div class="section-title mb-1">
                        <i class="bi bi-file-earmark-text-fill"></i> Təkliflər (<span id="detailQuotesCount">0</span>)
                    </div>
                    <div class="section-desc mb-2">Daşıyıcıların göndərdiyi qiymət təklifləri.</div>
                    <div id="detailQuotesContainer">
                        <p class="text-muted small">Təkliflər yüklənir...</p>
                    </div>
                </div>

                <!-- RFQ PAYLAŞIM MƏLUMATI -->
                <div class="card mb-3">
                    <div class="section-title mb-1">
                        <i class="bi bi-envelope-fill"></i> RFQ paylaşım məlumatı
                    </div>
                    <div class="row g-3 align-items-center">
                        <div class="col-12 col-md-7">
                            <div class="mb-2"><span class="text-muted small">Göndərən:</span> <strong class="text-dark ms-1" id="detailSenderCompany">—</strong></div>
                            <div class="mb-2"><span class="text-muted small">Göndərən email:</span> <strong class="text-dark ms-1" id="detailSenderEmail">—</strong></div>
                            <div class="mb-2"><span class="text-muted small">Reply-To:</span> <strong class="text-dark ms-1" id="detailReplyTo">—</strong></div>
                            <div class="mb-0"><span class="text-muted small">Email şablonu:</span> <strong class="text-dark ms-1" id="detailEmailTemplate">Standart şablon</strong></div>
                        </div>
                        <div class="col-12 col-md-5">
                            <div class="envelope-box">
                                <i class="bi bi-send-check-fill" style="font-size: 56px; color: var(--primary-blue); opacity: .85;"></i>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- CAVABSIZ DAŞIYICI XƏBƏRDARLIĞI -->
                <div id="detailNonResponders" class="alert alert-light border rounded-4 p-3 d-none align-items-center justify-content-between flex-wrap gap-2">
                    <span class="text-muted small mb-0"><i class="bi bi-info-circle text-primary me-1"></i> Bu RFQ üçün <strong id="detailPendingCount">0</strong> daşıyıcı hələ təklif göndərməyib. (<span id="detailSelectedCount">0</span> seçilib)</span>
                    <button type="button" class="btn btn-primary btn-sm rounded-pill px-3 w-100 w-sm-auto" onclick="sendSelectedReminders()">
                        <i class="bi bi-send me-1"></i> Seçilənləri reminder göndər
                    </button>
                </div>

            </div>
        </div>
    </div>

    <!-- DAŞIYICILAR PANELİ (bütün ekran ölçülərində sürüşən panel) -->
    <div class="offcanvas offcanvas-end" tabindex="-1" id="carriersPanel">
        <div class="offcanvas-header border-bottom">
            <h5 class="offcanvas-title fw-bold text-dark" style="font-size: 1rem;">
                Daşıyıcılar (<span id="panelCarriersCount">0</span>)
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
        </div>
        <div class="offcanvas-body d-flex flex-column p-3">
            <div class="input-group input-group-sm mb-2">
                <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input type="text" id="carrierPanelSearch" class="form-control border-start-0" placeholder="Daşıyıcı axtar..." oninput="renderCarrierPanel()">
            </div>

            <div class="d-flex gap-2 mb-3 flex-wrap">
                <span class="filter-pill active" id="filterPillAll" onclick="setCarrierPanelFilter('all')">Hamısı (<span id="tabAllCount">0</span>)</span>
                <span class="filter-pill" id="filterPillResponded" onclick="setCarrierPanelFilter('responded')">Təklif alanlar (<span id="tabRespondedCount">0</span>)</span>
                <span class="filter-pill" id="filterPillPending" onclick="setCarrierPanelFilter('pending')">Təklif almayanlar (<span id="tabPendingCount">0</span>)</span>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-2">
                <button type="button" class="btn btn-link btn-sm p-0 text-decoration-none fw-semibold" style="font-size: 12px;" onclick="selectAllPendingReminders()">Hamısını seç</button>
                <button type="button" class="btn btn-link btn-sm p-0 text-decoration-none fw-semibold text-muted" style="font-size: 12px;" onclick="clearAllReminderSelection()">Seçimi ləğv et</button>
            </div>

            <div id="carriersPanelList" class="flex-grow-1" style="overflow-y: auto; max-height: 55vh;">
                <p class="text-muted small">Daşıyıcılar yüklənir...</p>
            </div>

            <button type="button" class="btn btn-primary w-100 mt-3 rounded-pill" onclick="sendSelectedReminders()">
                <i class="bi bi-send me-1"></i> Seçilənləri reminder göndər (<span id="panelSelectedCount">0</span>)
            </button>
            <button type="button" class="btn btn-outline-secondary w-100 mt-2 rounded-pill" data-bs-dismiss="offcanvas">Bağla</button>
        </div>
    </div>

    <!-- RFQ ƏLAVƏ DETALLAR MODALI -->
    <div class="modal fade" id="requestExtraModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable mx-2 mx-sm-auto">
            <div class="modal-content">
                <div class="modal-header d-flex justify-content-between align-items-center">
                    <h5 class="modal-title fw-bold text-dark mb-0" style="font-size: 1.05rem;">
                        <i class="bi bi-info-circle-fill text-primary me-2"></i> RFQ-nun Əlavə Detalları
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="requestExtraModalContent"></div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary px-3 py-1.5 fw-semibold rounded-pill w-100 w-sm-auto" style="font-size: 13px;" data-bs-dismiss="modal">Bağla</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        let user = null;
        try {
            user = JSON.parse(localStorage.getItem("user"));
        } catch (e) {
            user = null;
        }

        const currentUserId = (user && user.id) ? user.id : 1;
        
        if (user && user.id) {
            document.getElementById("userCompanyName").innerText = user.company_name || user.email || "Müştəri";
        } else {
            document.getElementById("userCompanyName").innerText = "Test Müştəri (ID: 1)";
        }

        loadStats();
        loadRequests();
        loadCarriersList();
        loadManageCarriersList();

        let globalRequestsCache = [];
        let globalCarriersCache = [];

        function getCustomerId() {
            let u = null;
            try { u = JSON.parse(localStorage.getItem("user")); } catch(e) {}
            let rawId = (u && u.id) ? u.id : (typeof currentUserId !== 'undefined' ? currentUserId : 1);
            let cleaned = parseInt(String(rawId).replace(/[^0-9]/g, ''));
            return isNaN(cleaned) ? 1 : cleaned;
        }

        function formatErrorDetail(errDetail) {
            if (!errDetail) return "Naməlum xəta";
            if (typeof errDetail === 'string') return errDetail;
            if (Array.isArray(errDetail)) {
                return errDetail.map(err => err.msg || JSON.stringify(err)).join(", ");
            }
            if (typeof errDetail === 'object') {
                return JSON.stringify(errDetail);
            }
            return String(errDetail);
        }

        function logout() {
            localStorage.removeItem("user");
            window.location.replace("/login");
        }

        function toggleCarrierSelection() {
            const sendToSelected = document.getElementById("sendToSelectedRadio");
            const container = document.getElementById("carrierSelectionContainer");
            if (!sendToSelected || !container) return;
            
            if (sendToSelected.checked) {
                container.classList.remove("d-none");
            } else {
                container.classList.add("d-none");
            }
        }

        function toggleEmailTemplateFields() {
            const useCustom = document.getElementById("customTemplateRadio");
            const container = document.getElementById("customEmailContainer");
            if (!useCustom || !container) return;

            if (useCustom.checked) {
                container.classList.remove("d-none");
            } else {
                container.classList.add("d-none");
                const customBody = document.getElementById("custom_email_body");
                if (customBody) customBody.value = "";
            }
        }

        function toggleOptField(key) {
            const chk = document.getElementById(`chk_${key}`);
            if (!chk) return;

            if (key === 'info') {
                const container = document.getElementById(`inp_info_container`);
                if (!container) return;
                if (chk.checked) {
                    container.classList.remove('d-none');
                } else {
                    container.classList.add('d-none');
                    const infoText = document.getElementById(`inp_info_text`);
                    const infoFile = document.getElementById(`inp_info_file`);
                    if (infoText) infoText.value = '';
                    if (infoFile) infoFile.value = '';
                }
            } else {
                const input = document.getElementById(`inp_${key}`);
                if (!input) return;
                if (chk.checked) {
                    input.classList.remove('d-none');
                } else {
                    input.classList.add('d-none');
                    input.value = '';
                }
            }
        }

        function selectAllCarriers(select) {
            const checkboxes = document.querySelectorAll(".carrier-item-check");
            checkboxes.forEach(cb => cb.checked = select);
        }

        async function loadCarriersList() {
            try {
                const customerId = getCustomerId();
                const res = await fetch(`/carriers/customer/${customerId}`);
                const data = await res.json();
                const box = document.getElementById("carrierCheckboxList");
                
                let carriers = [];
                if (Array.isArray(data)) {
                    carriers = data;
                } else if (data.carriers && Array.isArray(data.carriers)) {
                    carriers = data.carriers;
                } else if (data.data && Array.isArray(data.data)) {
                    carriers = data.data;
                }

                if (res.ok && carriers.length > 0) {
                    let html = "";
                    for (let c of carriers) {
                        let carrierId = c.id !== undefined ? c.id : (c.carrier_id !== undefined ? c.carrier_id : c._id);
                        html += `
                            <div class="carrier-item-row" onclick="document.getElementById('carrier_${carrierId}').click(); event.stopPropagation();">
                                <div class="form-check mb-0 w-100">
                                    <input class="form-check-input carrier-item-check me-2" type="checkbox" value="${carrierId}" id="carrier_${carrierId}" onclick="event.stopPropagation();">
                                    <label class="form-check-label fw-bold text-dark text-break" for="carrier_${carrierId}" style="cursor: pointer;">
                                        ${c.company_name || c.name || c.carrier_name || 'Şirkət adı yoxdur'} <span class="text-muted fw-normal small ms-1">(${c.email || ''})</span>
                                    </label>
                                </div>
                            </div>
                        `;
                    }
                    box.innerHTML = html;
                } else {
                    box.innerHTML = `<span class="text-danger small p-2 d-block">Bazada daşıyıcı tapılmadı.</span>`;
                }
            } catch (err) {
                console.error("Daşıyıcılar yüklənmədi:", err);
                document.getElementById("carrierCheckboxList").innerHTML = `<span class="text-danger small p-2 d-block">Şəbəkə xətası baş verdi.</span>`;
            }
        }

        async function loadManageCarriersList() {
            try {
                const customerId = getCustomerId();
                const res = await fetch(`/carriers/customer/${customerId}`);
                const data = await res.json();
                
                let carriers = [];
                if (Array.isArray(data)) {
                    carriers = data;
                } else if (data.carriers && Array.isArray(data.carriers)) {
                    carriers = data.carriers;
                } else if (data.data && Array.isArray(data.data)) {
                    carriers = data.data;
                }

                if (res.ok) {
                    globalCarriersCache = carriers;
                    renderManageCarriers(carriers);
                } else {
                    document.getElementById("manageCarriersContainer").innerHTML = `<span class="text-muted small p-3 d-block text-center">Bazada hələ heç bir daşıyıcı yoxdur.</span>`;
                }
            } catch (err) {
                console.error("Daşıyıcılar idarəetmə siyahısı yüklənmədi:", err);
                document.getElementById("manageCarriersContainer").innerHTML = `<span class="text-danger small p-3 d-block text-center">Məlumatları yükləmək mümkün olmadı.</span>`;
            }
        }

        function renderManageCarriers(carriers) {
            const box = document.getElementById("manageCarriersContainer");
            if (!carriers || carriers.length === 0) {
                box.innerHTML = `<span class="text-muted small p-3 d-block text-center">Uyğun daşıyıcı tapılmadı.</span>`;
                return;
            }

            let html = "";
            for (let c of carriers) {
                let carrierId = c.id !== undefined ? c.id : (c.carrier_id !== undefined ? c.carrier_id : c._id);
                html += `
                    <div class="carrier-item-row d-flex justify-content-between align-items-center flex-wrap gap-2">
                        <div class="text-break" style="max-width: 70%;">
                            <strong class="text-dark">${c.company_name || c.name || c.carrier_name || 'Şirkət adı yoxdur'}</strong> 
                            <span class="text-muted small ms-1">(${c.email || 'Email yoxdur'})</span>
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-danger py-1 px-2" style="font-size: 12px;" onclick="deleteCarrier(${carrierId})">
                            <i class="bi bi-trash3-fill me-1"></i> Sil
                        </button>
                    </div>
                `;
            }
            box.innerHTML = html;
        }

        // YENİLİK: Daşıyıcı filtrləmə funksiyası
        function filterManageCarriers() {
            const query = document.getElementById("carrierSearchInput").value.toLowerCase();
            const filtered = globalCarriersCache.filter(c => {
                const name = (c.company_name || c.name || c.carrier_name || '').toLowerCase();
                const email = (c.email || '').toLowerCase();
                return name.includes(query) || email.includes(query);
            });
            renderManageCarriers(filtered);
        }

        async function deleteCarrier(carrierId) {
            if (!confirm("Bu daşıyıcını bazanızdan silmək istədiyinizə əminsiniz?")) return;
            try {
                const customerId = getCustomerId();
                const res = await fetch(`/carriers/delete`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ customer_id: customerId, carrier_id: carrierId })
                });

                if (res.ok) {
                    alert("Daşıyıcı bazadan uğurla silindi!");
                    loadManageCarriersList();
                    loadCarriersList();
                    loadStats();
                } else {
                    const errData = await res.json().catch(() => ({}));
                    alert("Silinmə zamanı xəta baş verdi: " + formatErrorDetail(errData.detail));
                }
            } catch (err) {
                console.error("Silmə xətası:", err);
                alert("Serverlə əlaqə qurulmadı!");
            }
        }

        async function uploadCarriers(e) {
            e.preventDefault();
            const fileInput = document.querySelector("#file-content input[name='file']");
            if (!fileInput || !fileInput.files.length) {
                alert("Zəhmət olmasa Excel və ya CSV faylı seçin!");
                return;
            }

            const customerId = getCustomerId();
            const formData = new FormData();
            formData.append("customer_id", customerId);
            formData.append("file", fileInput.files[0]);

            try {
                const res = await fetch("/carriers/upload-excel", {
                    method: "POST",
                    body: formData
                });
                const data = await res.json();
                if (res.ok) {
                    alert(data.message || "Fayl uğurla yükləndi!");
                    fileInput.value = "";
                    loadStats();
                    loadCarriersList();
                    loadManageCarriersList();
                } else {
                    alert("Xəta: " + formatErrorDetail(data.detail));
                }
            } catch (err) {
                console.error("Yükləmə xətası:", err);
                alert("Serverlə əlaqə qurulmadı!");
            }
        }

        async function addManualCarrier(e) {
            e.preventDefault();
            const name = document.getElementById("manual_company_name").value.trim();
            const email = document.getElementById("manual_email").value.trim();

            if (!name || !email) {
                alert("Zəhmət olmasa bütün xanaları doldurun!");
                return;
            }

            const customerId = getCustomerId();

            try {
                const res = await fetch("/carriers/manual", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ 
                        customer_id: customerId, 
                        name: name, 
                        company_name: name, 
                        carrier_name: name,
                        email: email 
                    })
                });
                const data = await res.json();
                if (res.ok) {
                    alert("Daşıyıcı uğurla əlavə edildi!");
                    document.getElementById("manual_company_name").value = "";
                    document.getElementById("manual_email").value = "";
                    loadStats();
                    loadCarriersList();
                    loadManageCarriersList();
                } else {
                    alert("Xəta: " + formatErrorDetail(data.detail));
                }
            } catch (err) {
                console.error("Daşıyıcı əlavə etmə xətası:", err);
                alert("Serverlə əlaqə qurulmadı!");
            }
        }

        async function addPasteCarrier(e) {
            e.preventDefault();
            const text = document.getElementById("paste_raw_text").value.trim();
            if (!text) {
                alert("Zəhmət olmasa cədvəl məlumatlarını yapışdırın!");
                return;
            }

            const customerId = getCustomerId();

            try {
                const res = await fetch("/carriers/upload-text", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ 
                        customer_id: customerId, 
                        raw_text: text, 
                        text: text,
                        content: text
                    })
                });
                const data = await res.json();
                if (res.ok) {
                    alert("Daşıyıcılar uğurla əlavə edildi!");
                    document.getElementById("paste_raw_text").value = "";
                    loadStats();
                    loadCarriersList();
                    loadManageCarriersList();
                } else {
                    alert("Xəta: " + formatErrorDetail(data.detail));
                }
            } catch (err) {
                console.error("Cədvəldən əlavə etmə xətası:", err);
                alert("Serverlə əlaqə qurulmadı!");
            }
        }

        async function loadStats() {
            try {
                const customerId = getCustomerId();
                const res = await fetch(`/customer/stats/${customerId}`);
                const data = await res.json();
                if (res.ok) {
                    document.getElementById("statActiveRfqs").innerText = data.active_rfqs || 0;
                    document.getElementById("statCompleted").innerText = data.completed_shipments || 0;
                    document.getElementById("statCarriersCount").innerText = data.carriers_count || 0;
                }
            } catch (err) {
                console.error("Statistika xətası:", err);
            }
        }

        async function createRfq(e) {
            e.preventDefault();

            const sendToAll = document.getElementById("sendToAllRadio").checked;
            let selectedCarriers = [];
            
            if (!sendToAll) {
                const checkboxes = document.querySelectorAll(".carrier-item-check:checked");
                checkboxes.forEach(cb => {
                    const carrierId = parseInt(cb.value);
                    if (!isNaN(carrierId)) {
                        selectedCarriers.push(carrierId);
                    }
                });

                if (selectedCarriers.length === 0) {
                    alert("Zəhmət olmasa siyahıdan ən azı bir daşıyıcı seçin və ya 'Bütün daşıyıcılara göndər' seçin!");
                    return;
                }
            }

            let uploadedAttachmentUrl = null;
            let fileToUpload = null;

            if (document.getElementById("chk_info")?.checked) {
                const fileInp = document.getElementById("inp_info_file");
                if (fileInp && fileInp.files.length > 0) {
                    fileToUpload = fileInp.files[0];
                }
            }

            if (fileToUpload) {
                const fileData = new FormData();
                fileData.append("file", fileToUpload);

                try {
                    const uploadRes = await fetch("/requests/upload-attachment", {
                        method: "POST",
                        body: fileData
                    });
                    const uploadResult = await uploadRes.json();
                    if (uploadRes.ok) {
                        uploadedAttachmentUrl = uploadResult.attachment_url;
                    } else {
                        alert("Fayl yüklənərkən xəta baş verdi: " + formatErrorDetail(uploadResult.detail));
                        return;
                    }
                } catch (fileErr) {
                    console.error("Fayl yükləmə xətası:", fileErr);
                    alert("Faylı serverə yükləmək mümkün olmadı!");
                    return;
                }
            }

            const requiredFieldsList = [];

            if(document.getElementById("chk_loading_date")?.checked) {
                let val = document.getElementById("inp_loading_date")?.value.trim();
                if(val) requiredFieldsList.push(`Loading Date: ${val}`);
            }
            if(document.getElementById("chk_truck_type")?.checked) {
                let val = document.getElementById("inp_truck_type")?.value.trim();
                if(val) requiredFieldsList.push(`Truck Type: ${val}`);
            }
            if(document.getElementById("chk_volume")?.checked) {
                let val = document.getElementById("inp_volume")?.value.trim();
                if(val) requiredFieldsList.push(`Volume (CBM): ${val}`);
            }
            if(document.getElementById("chk_hs_code")?.checked) {
                let val = document.getElementById("inp_hs_code")?.value.trim();
                if(val) requiredFieldsList.push(`HS Code: ${val}`);
            }
            if(document.getElementById("chk_stackable")?.checked) {
                let val = document.getElementById("inp_stackable")?.value;
                if(val) requiredFieldsList.push(`Stackable / Non-stackable: ${val}`);
            }
            if(document.getElementById("chk_shipment_type")?.checked) {
                let val = document.getElementById("inp_shipment_type")?.value.trim();
                if(val) requiredFieldsList.push(`Shipment Type: ${val}`);
            }
            if(document.getElementById("chk_incoterm")?.checked) {
                let val = document.getElementById("inp_incoterm")?.value.trim();
                if(val) requiredFieldsList.push(`Incoterm: ${val}`);
            }
            if(document.getElementById("chk_adr")?.checked) {
                let val = document.getElementById("inp_adr")?.value.trim();
                if(val) requiredFieldsList.push(`Dangerous Goods (ADR): ${val}`);
            }
            if(document.getElementById("chk_temp")?.checked) {
                let val = document.getElementById("inp_temp")?.value.trim();
                if(val) requiredFieldsList.push(`Temperature Requirement: ${val}`);
            }
            if(document.getElementById("chk_deliv_date")?.checked) {
                let val = document.getElementById("inp_deliv_date")?.value.trim();
                if(val) requiredFieldsList.push(`Delivery Deadline: ${val}`);
            }
            if(document.getElementById("chk_info")?.checked) {
                let textVal = document.getElementById("inp_info_text")?.value.trim() || "";
                let fileInput = document.getElementById("inp_info_file");
                let infoStr = textVal;
                if(fileInput && fileInput.files.length > 0) {
                    infoStr += ` [Fayl: ${fileInput.files[0].name}]`;
                }
                if(infoStr) requiredFieldsList.push(`Additional Information: ${infoStr}`);
            }

            const customerId = getCustomerId();
            
            const originVal = document.getElementById("origin")?.value.trim();
            const destinationVal = document.getElementById("destination")?.value.trim();
            const cargoTypeVal = document.getElementById("cargo_type")?.value.trim();
            const weightVal = document.getElementById("weight_kg")?.value;
            const transportModeVal = document.getElementById("transportation_mode")?.value;

            if (!originVal || !destinationVal || !cargoTypeVal || !weightVal || !transportModeVal) {
                alert("Zəhmət olmasa bütün məcburi (*) sahələri doldurun!");
                return;
            }

            let additionalNotesCombined = "";
            if(document.getElementById("chk_info")?.checked) {
                additionalNotesCombined = document.getElementById("inp_info_text")?.value.trim() || "";
            }

            const useCustomTemplate = document.getElementById("customTemplateRadio").checked;
            const customEmailBodyVal = useCustomTemplate ? (document.getElementById("custom_email_body")?.value.trim() || "") : "";

            const payload = {
                customer_id: customerId,
                origin: originVal,
                loading_location: originVal,
                destination: destinationVal,
                delivery_location: destinationVal,
                cargo_type: cargoTypeVal,
                cargo: cargoTypeVal,
                weight_kg: parseFloat(weightVal) || 0,
                weight: parseFloat(weightVal) || 0,
                volume_m3: document.getElementById("chk_volume")?.checked ? (parseFloat(document.getElementById("inp_volume")?.value) || 0) : 0,
                volume: document.getElementById("chk_volume")?.checked ? (parseFloat(document.getElementById("inp_volume")?.value) || 0) : 0,
                deadline: document.getElementById("chk_loading_date")?.checked ? (document.getElementById("inp_loading_date")?.value || "") : "",
                loading_date: document.getElementById("chk_loading_date")?.checked ? (document.getElementById("inp_loading_date")?.value || "") : "",
                truck_type: document.getElementById("chk_truck_type")?.checked ? (document.getElementById("inp_truck_type")?.value || "") : "",
                hs_code: document.getElementById("chk_hs_code")?.checked ? (document.getElementById("inp_hs_code")?.value || "") : "",
                stackable: document.getElementById("chk_stackable")?.checked ? (document.getElementById("inp_stackable")?.value || "") : "",
                shipment_type: document.getElementById("chk_shipment_type")?.checked ? (document.getElementById("inp_shipment_type")?.value || "") : "",
                required_fields: requiredFieldsList,
                send_to_all: sendToAll,
                carrier_ids: sendToAll ? [] : selectedCarriers,
                attachment_url: uploadedAttachmentUrl,
                additional_notes: additionalNotesCombined,
                note: additionalNotesCombined,
                email_template_type: useCustomTemplate ? "custom" : "standard",
                custom_email_body: customEmailBodyVal,
                transportation_mode: transportModeVal,
            };

            try {
                const res = await fetch("/requests/create", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok) {
                    let msg = typeof data.message === 'object' ? JSON.stringify(data.message) : (data.message || "Sorğu uğurla yaradıldı!");
                    alert(msg);
                    
                    document.getElementById("rfqForm").reset();
                    document.querySelectorAll('.opt-input').forEach(el => el.classList.add('d-none'));
                    const infoContainer = document.getElementById('inp_info_container');
                    if(infoContainer) infoContainer.classList.add('d-none');
                    document.getElementById("sendToAllRadio").checked = true;
                    document.getElementById("standardTemplateRadio").checked = true;
                    toggleEmailTemplateFields();
                    toggleCarrierSelection();
                    loadStats();
                    loadRequests();
                } else {
                    alert("Xəta: " + formatErrorDetail(data.detail));
                }
            } catch (err) {
                console.error(err);
                alert("Server xətası!");
            }
        }

        async function loadRequests() {
            const container = document.getElementById("requestsContainer");
            container.innerHTML = `<div class="text-center p-3"><span class="spinner-border spinner-border-sm text-primary me-2"></span><span class="text-muted small">Sorğular yüklənir...</span></div>`;
            try {
                const customerId = getCustomerId();
                const res = await fetch(`/requests/customer/${customerId}`);
                const data = await res.json();
                
                let requestsList = [];
                if (Array.isArray(data)) {
                    requestsList = data;
                } else if (data && Array.isArray(data.requests)) {
                    requestsList = data.requests;
                }

                if (res.ok) {
                    globalRequestsCache = requestsList;
                    renderRequests(requestsList);
                } else {
                    container.innerHTML = `<div class="alert alert-light border text-center p-4 rounded-4"><i class="bi bi-inbox fs-2 text-muted d-block mb-2"></i><span class="text-muted fw-medium small">Hələ heç bir sorğu yaratmamısınız.</span></div>`;
                }
            } catch (err) {
                container.innerHTML = `<p class="text-danger fw-bold small"><i class="bi bi-exclamation-circle-fill me-1"></i> Sorğuları yükləmək mümkün olmadı.</p>`;
            }
        }

        function renderRequests(requestsList) {
            const container = document.getElementById("requestsContainer");
            if (!requestsList || requestsList.length === 0) {
                container.innerHTML = `<div class="alert alert-light border text-center p-4 rounded-4"><i class="bi bi-inbox fs-2 text-muted d-block mb-2"></i><span class="text-muted fw-medium small">Uyğun sorğu tapılmadı.</span></div>`;
                return;
            }

            let html = "";
            for (let req of requestsList) {
                let attachmentBtn = "";
                if (req.attachment_url) {
                    attachmentBtn = `<a href="${req.attachment_url}" target="_blank" class="btn btn-sm btn-light mt-2 mt-sm-0 fw-semibold border rounded-pill px-3" style="font-size: 11.5px;"><i class="bi bi-paperclip text-primary"></i> Sənədə Bax</a>`;
                }

                let qCount = req.quotes_count !== undefined && req.quotes_count !== null ? req.quotes_count : 0;
                let badgeClass = qCount > 0 ? 'bg-info text-dark' : 'bg-secondary';
                
                let bgClass = req.status === 'open' ? 'bg-primary' : 'bg-success';
                let statusText = (req.status || 'Aktiv').toUpperCase();

                let deadlineField = req.deadline ? `<div class="col-12 col-sm-4"><i class="bi bi-calendar-event me-1 text-primary"></i> Yükləmə: <strong class="text-dark">${req.deadline}</strong></div>` : '';

                html += `
                    <div class="request-card">
                        <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-3 gap-2">
                            <h6 class="fw-bold text-dark mb-0 d-flex align-items-center fs-6 flex-wrap gap-1">
                                <span class="badge bg-light text-secondary border shadow-sm">ID: ${req.id}</span> 
                                <span class="text-break">${req.origin || req.loading_location || ''}</span> 
                                <i class="bi bi-arrow-right-short mx-1 text-primary fs-5"></i> 
                                <span class="text-break">${req.destination || req.delivery_location || ''}</span>
                            </h6>
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge ${badgeClass} shadow-sm">${qCount} təklif</span>
                                <span class="badge ${bgClass} shadow-sm">${statusText}</span>
                            </div>
                        </div>
                        <div class="request-meta-box mb-3">
                            <div class="row text-muted small fw-medium g-2">
                                <div class="col-12 col-sm-4"><i class="bi bi-box-seam me-1 text-primary"></i> Növ: <strong class="text-dark">${req.cargo_type || req.cargo || ''}</strong></div>
                                <div class="col-12 col-sm-4"><i class="bi bi-speedometer2 me-1 text-primary"></i> Çəki: <strong class="text-dark">${req.weight_kg || req.weight || 0} kq</strong></div>
                                ${deadlineField}
                            </div>
                        </div>
                        <div id="quotes-for-${req.id}" class="mt-2 d-flex align-items-center flex-wrap gap-2">
                            <button class="btn btn-sm btn-primary px-3 py-1.5 fw-bold rounded-pill shadow-sm" style="font-size: 12px;" onclick="openRfqDetail(${req.id})">
                                <i class="bi bi-eye me-1"></i> RFQ-ya Bax (${qCount} təklif)
                            </button>
                            ${attachmentBtn}
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }

        // YENİLİK: Sorğu filtrləmə funksiyası
        function filterRequests() {
            const query = document.getElementById("requestSearchInput").value.toLowerCase();
            const filtered = globalRequestsCache.filter(req => {
                const origin = (req.origin || req.loading_location || '').toLowerCase();
                const destination = (req.destination || req.delivery_location || '').toLowerCase();
                const cargo = (req.cargo_type || req.cargo || '').toLowerCase();
                const idStr = String(req.id || '').toLowerCase();
                return origin.includes(query) || destination.includes(query) || cargo.includes(query) || idStr.includes(query);
            });
            renderRequests(filtered);
        }

        window.currentQuotesCache = {};

        function buildQuotesTableHtml(quotesList, requestId) {
            if (!quotesList || quotesList.length === 0) {
                return `<div class="alert alert-light mt-2 border rounded-3 p-2.5 w-100"><p class="text-muted small mb-0"><i class="bi bi-info-circle me-1"></i> Hələ bu sorğuya təklif göndərilməyib.</p></div>`;
            }

            let html = `<div class="table-container-responsive rounded-4 overflow-hidden border shadow-sm w-100"><table class="table table-hover bg-white align-middle small mb-0">
                <thead style="background: #f8fafc;">
                    <tr>
                        <th class="py-2.5 px-3 text-muted fw-bold">Daşıyıcı Şirkət</th>
                        <th class="py-2.5 px-3 text-muted fw-bold">Qiymət</th>
                        <th class="py-2.5 px-3 text-muted fw-bold">Müddət</th>
                        <th class="py-2.5 px-3 text-muted fw-bold">Qeydlər</th>
                        <th class="py-2.5 px-3 text-muted fw-bold text-center">Əməliyyat</th>
                    </tr>
                </thead>
                <tbody>`;

            for (let q of quotesList) {
                let extraStr = "";
                if (q.extra_details) {
                    for (let [k, v] of Object.entries(q.extra_details)) {
                        if (k === 'submitted' || k.toLowerCase() === 'submitted' || k.toLowerCase() === 'carrier_attachment_name') continue;

                        if (v !== null && v !== undefined && v !== "") {
                            if (k === 'carrier_attachment_url') {
                                extraStr += `<div><strong class="text-dark">Sənəd:</strong> <a href="${v}" target="_blank" class="text-primary fw-bold text-decoration-none"><i class="bi bi-link-45deg"></i> Bax</a></div>`;
                            } else {
                                extraStr += `<div><strong class="text-dark">${k}:</strong> ${v}</div>`;
                            }
                        }
                    }
                }

                let transitDisplay = (q.transit_time_days !== null && q.transit_time_days !== undefined && q.transit_time_days !== "null") 
                    ? `${q.transit_time_days} gün` 
                    : `<span class="text-muted fst-italic">Qeyd olunmayıb</span>`;

                let priceDisplay = (q.price !== null && q.price !== undefined && q.price !== "null") 
                    ? `${q.price} <span class="text-muted small">${q.currency || 'AZN'}</span>` 
                    : `<span class="text-muted fst-italic">Qiymət yoxdur</span>`;

                html += `
                    <tr class="${q.is_winner ? 'table-success' : ''}">
                        <td class="px-3 fw-bold text-dark py-2.5" style="min-width: 130px;">${q.carrier_company || 'Daşıyıcı'}</td>
                        <td class="px-3 text-success fw-bold py-2.5" style="min-width: 100px;">${priceDisplay}</td>
                        <td class="px-3 fw-medium text-dark py-2.5" style="min-width: 90px;">${transitDisplay}</td>
                        <td class="px-3 py-2.5" style="min-width: 160px;">
                            <div class="text-muted mb-1 text-truncate" style="max-width: 180px;">${extraStr || 'Məlumat yoxdur'}</div>
                            <button class="btn btn-link btn-sm p-0 text-primary fw-bold text-decoration-none text-nowrap" style="font-size: 11.5px;" onclick="openQuoteModal(${requestId}, ${q.id})">
                                Daha Ətraflı <i class="bi bi-arrow-right-short"></i>
                            </button>
                        </td>
                        <td class="px-3 text-center py-2.5" style="min-width: 100px;">
                            ${q.is_winner ? 
                                '<span class="badge bg-success px-2.5 py-1 rounded-pill"><i class="bi bi-trophy-fill me-1"></i> Qalib</span>' : 
                                `<button class="btn btn-sm btn-outline-success fw-bold rounded-pill px-2.5 py-1" style="font-size: 11.5px;" onclick="selectWinner(${requestId}, ${q.id})">Qalib Seç</button>`
                            }
                        </td>
                    </tr>
                `;
            }
            html += `</tbody></table></div>`;
            return html;
        }

        async function loadQuotesInto(requestId, container) {
            if (!container) return;
            container.innerHTML = `<div class="mt-2 p-2 text-center w-100"><span class="spinner-border spinner-border-sm text-primary me-2"></span> <span class="text-muted fw-medium small">Təkliflər yüklənir...</span></div>`;

            try {
                const res = await fetch(`/quotes/request/${requestId}`);
                const data = await res.json();

                let quotesList = [];
                if (Array.isArray(data)) {
                    quotesList = data;
                } else if (data && Array.isArray(data.quotes)) {
                    quotesList = data.quotes;
                }

                if (res.ok) {
                    window.currentQuotesCache[requestId] = quotesList;
                    container.innerHTML = buildQuotesTableHtml(quotesList, requestId);
                } else {
                    container.innerHTML = `<p class="text-danger small mt-2 fw-bold"><i class="bi bi-x-circle me-1"></i> Təklifləri yükləmək xətası.</p>`;
                }
                return quotesList;
            } catch (err) {
                container.innerHTML = `<p class="text-danger small mt-2 fw-bold"><i class="bi bi-x-circle me-1"></i> Təklifləri yükləmək xətası.</p>`;
                return [];
            }
        }

        async function loadQuotes(requestId) {
            const quotesDiv = document.getElementById(`quotes-for-${requestId}`);
            await loadQuotesInto(requestId, quotesDiv);
        }

        async function loadDetailQuotes(requestId) {
            const container = document.getElementById("detailQuotesContainer");
            const quotesList = await loadQuotesInto(requestId, container);
            const countEl = document.getElementById("detailQuotesCount");
            if (countEl) countEl.textContent = quotesList.length;
        }

        function openQuoteModal(requestId, quoteId) {
            const quotes = window.currentQuotesCache[requestId] || [];
            const q = quotes.find(item => item.id === quoteId);
            if (!q) return;

            let extraHtml = "";
            if (q.extra_details) {
                for (let [k, v] of Object.entries(q.extra_details)) {
                    if (k === 'submitted') continue;

                    if (v !== null && v !== undefined && v !== "" && v !== "null") {
                        if (k === 'carrier_attachment_url') {
                            extraHtml += `<div class="mb-2 p-2.5 rounded-3 border bg-white shadow-sm d-flex justify-content-between align-items-center flex-wrap gap-2">
                                <strong class="text-dark small">Qoşulmuş Fayl:</strong>
                                <a href="${v}" target="_blank" class="btn btn-sm btn-primary rounded-pill px-3" style="font-size: 12px;"><i class="bi bi-cloud-download me-1"></i> Yüklə</a>
                            </div>`;
                        } else {
                            extraHtml += `<div class="mb-2 p-2.5 rounded-3 border bg-white shadow-sm">
                                <strong class="text-primary text-uppercase small tracking-wider mb-1 d-block" style="font-size: 10.5px;">${k}</strong>
                                <p class="mb-0 text-dark fw-medium small text-break" style="white-space: pre-wrap;">${v}</p>
                            </div>`;
                        }
                    }
                }
            }

            let modalTransitDisplay = (q.transit_time_days !== null && q.transit_time_days !== undefined && q.transit_time_days !== "null")
                ? `${q.transit_time_days} <span class="fs-6 text-muted">gün</span>`
                : `<span class="fs-6 text-muted fst-italic">Qeyd olunmayıb</span>`;

            let modalPriceDisplay = (q.price !== null && q.price !== undefined && q.price !== "null")
                ? `${q.price} <span class="fs-6 text-muted">${q.currency || 'AZN'}</span>`
                : `<span class="fs-6 text-muted fst-italic">Yoxdur</span>`;

            const modalContent = document.getElementById("modalQuoteContent");
            modalContent.innerHTML = `
                <div class="mb-3 text-center">
                    <span class="badge bg-light text-primary mb-1 px-2.5 py-1 border rounded-pill">Daşıyıcı Şirkət</span>
                    <h4 class="fw-bold text-dark text-break" style="font-size: 1.2rem;">${q.carrier_company || 'Daşıyıcı'}</h4>
                </div>
                <div class="row g-2 mb-3">
                    <div class="col-12 col-sm-6">
                        <div class="p-3 rounded-4 border bg-light h-100">
                            <span class="text-muted small fw-bold text-uppercase d-block mb-1" style="font-size: 10.5px;">Təklif olunan Qiymət</span>
                            <h3 class="text-success fw-bold mb-0 text-break" style="font-size: 1.3rem;">${modalPriceDisplay}</h3>
                        </div>
                    </div>
                    <div class="col-12 col-sm-6">
                        <div class="p-3 rounded-4 border bg-light h-100">
                            <span class="text-muted small fw-bold text-uppercase d-block mb-1" style="font-size: 10.5px;">Tranzit Müddəti</span>
                            <h3 class="text-dark fw-bold mb-0 text-break" style="font-size: 1.3rem;">${modalTransitDisplay}</h3>
                        </div>
                    </div>
                </div>
                <div class="p-3 rounded-4 bg-light">
                    <h6 class="fw-bold text-dark mb-2 small"><i class="bi bi-list-stars text-primary me-2"></i> Əlavə Məlumatlar və Şərtlər:</h6>
                    ${extraHtml || '<div class="p-2 border rounded-3 bg-white text-muted text-center small">Əlavə detal qeyd olunmayıb.</div>'}
                </div>
            `;

            const modal = new bootstrap.Modal(document.getElementById("quoteDetailModal"));
            modal.show();
        }

        async function selectWinner(requestId, quoteId) {
            if (!confirm("Bu təklifi qalib seçmək istədiyinizə əminsiniz?")) return;
            try {
                const res = await fetch("/quotes/select-winner", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ request_id: requestId, quote_id: quoteId })
                });
                const data = await res.json();
                if (res.ok) {
                    alert("Qalib təklif uğurla təsdiqləndi!");
                    loadRequests();
                    loadStats();
                    if (currentDetailRequestId === requestId) {
                        loadDetailQuotes(requestId);
                        loadDetailCarriersStatus(requestId);
                    }
                } else {
                    alert("Xəta: " + formatErrorDetail(data.detail));
                }
            } catch (err) {
                alert("Server xətası!");
            }
        }

        /* ================================================================
           RFQ DETAIL SƏHİFƏSİ
           ================================================================ */
        let currentDetailRequestId = null;
        let currentDetailRequestObj = null;
        let detailCarriersCache = [];
        let carrierPanelFilter = 'all';
        let selectedReminderIds = new Set();

        const AVATAR_PALETTE = ['#4f46e5', '#0ea5e9', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#ef4444', '#14b8a6'];

        function getInitials(name) {
            if (!name) return "?";
            const parts = String(name).trim().split(/\s+/).filter(Boolean);
            if (parts.length === 0) return "?";
            if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }

        async function openRfqDetail(requestId) {
            currentDetailRequestId = requestId;
            selectedReminderIds = new Set();

            document.getElementById("dashboardMain").classList.add("d-none");
            document.getElementById("rfqDetailPage").classList.remove("d-none");
            window.scrollTo(0, 0);

            let req = (globalRequestsCache || []).find(r => String(r.id) === String(requestId));
            if (!req) {
                try {
                    const res = await fetch(`/requests/details/${requestId}`);
                    const data = await res.json();
                    if (res.ok && data.request) req = data.request;
                } catch (err) { /* ignore, fallback below */ }
            }
            currentDetailRequestObj = req || { id: requestId };
            renderDetailHeader(currentDetailRequestObj);

            loadDetailQuotes(requestId);
            loadDetailCarriersStatus(requestId);
        }

        function closeRfqDetail() {
            document.getElementById("rfqDetailPage").classList.add("d-none");
            document.getElementById("dashboardMain").classList.remove("d-none");
            currentDetailRequestId = null;
            loadRequests();
            loadStats();
        }

        function refreshRfqDetail() {
            if (!currentDetailRequestId) return;
            loadDetailQuotes(currentDetailRequestId);
            loadDetailCarriersStatus(currentDetailRequestId);
        }

        function renderDetailHeader(req) {
            document.getElementById("detailBreadcrumbId").textContent = `RFQ #${req.id}`;
            document.getElementById("detailIdBadge").textContent = `ID: ${req.id}`;
            document.getElementById("detailOrigin").textContent = req.origin || req.loading_location || "—";
            document.getElementById("detailDestination").textContent = req.destination || req.delivery_location || "—";
            document.getElementById("detailCargoType").textContent = req.cargo_type || req.cargo || "—";

            const weight = req.weight_kg || req.weight;
            document.getElementById("detailWeight").textContent = weight ? `${weight} kq` : "Qeyd edilməyib";
            document.getElementById("detailDeadline").textContent = req.deadline || "Qeyd edilməyib";

            const statusBadge = document.getElementById("detailStatusBadge");
            const isOpen = (req.status || "open") === "open";
            statusBadge.textContent = isOpen ? "OPEN" : "CLOSED";
            statusBadge.className = `badge shadow-sm ${isOpen ? 'bg-primary' : 'bg-success'}`;

            document.getElementById("detailSenderCompany").textContent = (user && (user.company_name || user.name)) || "—";
            document.getElementById("detailSenderEmail").textContent = (user && user.email) || "—";
            document.getElementById("detailReplyTo").textContent = (user && user.email) || "—";
            document.getElementById("detailEmailTemplate").textContent = req.email_template_type === 'custom' ? "Fərdi şablon" : "Standart şablon";

            renderRequestExtraModal(req);
        }

        function renderRequestExtraModal(req) {
            const box = document.getElementById("requestExtraModalContent");
            const rows = [
                ["Daşınma növü / Truck type", req.truck_type],
                ["Yük tipi (Shipment type)", req.shipment_type],
                ["HS Kodu", req.hs_code],
                ["Həcm (m3)", req.volume_m3],
                ["Stiflənə bilər (Stackable)", req.stackable === true ? "Bəli" : (req.stackable === false ? "Xeyr" : null)],
                ["Əlavə qeydlər", req.additional_notes || req.note]
            ];

            let html = `<div class="d-flex flex-column gap-2">`;
            let hasAny = false;
            for (let [label, value] of rows) {
                if (value === null || value === undefined || value === "" || value === "Qeyd edilməyib") continue;
                hasAny = true;
                html += `<div class="p-2.5 rounded-3 border bg-light"><strong class="text-primary small d-block mb-1">${label}</strong><span class="text-dark small">${value}</span></div>`;
            }

            if (Array.isArray(req.required_fields) && req.required_fields.length > 0) {
                hasAny = true;
                html += `<div class="p-2.5 rounded-3 border bg-light"><strong class="text-primary small d-block mb-1">Tələb olunan sahələr</strong><span class="text-dark small">${req.required_fields.join(", ")}</span></div>`;
            }

            if (req.attachment_url) {
                hasAny = true;
                html += `<div class="p-2.5 rounded-3 border bg-light d-flex justify-content-between align-items-center flex-wrap gap-2"><strong class="text-primary small">Qoşulmuş sənəd</strong><a href="${req.attachment_url}" target="_blank" class="btn btn-sm btn-primary rounded-pill px-3"><i class="bi bi-cloud-download me-1"></i> Yüklə</a></div>`;
            }

            if (!hasAny) {
                html += `<div class="text-muted small text-center p-3">Əlavə detal qeyd olunmayıb.</div>`;
            }
            html += `</div>`;
            box.innerHTML = html;
        }

        async function checkBouncesNow() {
            const btn = document.getElementById("checkBouncesBtn");
            const originalHtml = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm" style="width:11px;height:11px;"></span> Yoxlanılır...`;

            try {
                const res = await fetch(`/quotes/check-bounces`, { method: "POST" });
                const data = await res.json();

                if (res.ok && data.status === "success") {
                    const count = (data.updated || []).length;
                    if (count > 0 && typeof showToast === "function") {
                        showToast(`${count} mail ünvanı çatdırılmayan olaraq tapıldı və yeniləndi.`, "success");
                    } else if (count === 0 && typeof showToast === "function") {
                        showToast("Yeni çatdırılmayan mail tapılmadı.", "info");
                    }
                    // Statistikanı təzələ
                    if (currentDetailRequestId) {
                        await loadDetailCarriersStatus(currentDetailRequestId);
                    }
                } else if (typeof showToast === "function") {
                    showToast("Bounce yoxlanışı zamanı xəta baş verdi.", "danger");
                }
            } catch (err) {
                if (typeof showToast === "function") {
                    showToast("Bounce yoxlanışı zamanı xəta baş verdi.", "danger");
                }
            } finally {
                btn.disabled = false;
                btn.innerHTML = originalHtml;
            }
        }

        async function loadDetailCarriersStatus(requestId) {
            const list = document.getElementById("carriersPanelList");
            list.innerHTML = `<div class="text-center p-3"><span class="spinner-border spinner-border-sm text-primary me-2"></span><span class="text-muted small">Daşıyıcılar yüklənir...</span></div>`;

            try {
                const res = await fetch(`/requests/carriers-status/${requestId}`);
                const data = await res.json();
                detailCarriersCache = (res.ok && Array.isArray(data.carriers)) ? data.carriers : [];

                selectedReminderIds = new Set(
                    detailCarriersCache.filter(c => !c.has_submitted).map(c => c.quote_id)
                );
                updateSelectedReminderCount();

                const total = detailCarriersCache.length;
                const delivered = detailCarriersCache.filter(c => c.mail_status === 'delivered').length;
                const viewed = detailCarriersCache.filter(c => c.is_viewed).length;
                const quoted = detailCarriersCache.filter(c => c.has_submitted).length;
                const failed = detailCarriersCache.filter(c => c.mail_status === 'failed').length;
                const pending = detailCarriersCache.filter(c => !c.has_submitted).length;

                document.getElementById("statSent").textContent = total;
                document.getElementById("statDelivered").textContent = delivered;
                document.getElementById("statViewed").textContent = viewed;
                document.getElementById("statQuoted").textContent = quoted;
                document.getElementById("statFailed").textContent = failed;

                document.getElementById("mobileCarriersCount").textContent = total;
                document.getElementById("statBtnCarriersCount").textContent = total;
                document.getElementById("panelCarriersCount").textContent = total;

                const pendingBanner = document.getElementById("detailNonResponders");
                document.getElementById("detailPendingCount").textContent = pending;
                if (pending > 0) {
                    pendingBanner.classList.remove("d-none");
                    pendingBanner.classList.add("d-flex");
                } else {
                    pendingBanner.classList.remove("d-flex");
                    pendingBanner.classList.add("d-none");
                }

                renderCarrierPanel();
            } catch (err) {
                list.innerHTML = `<p class="text-danger small fw-bold"><i class="bi bi-x-circle me-1"></i> Daşıyıcıları yükləmək mümkün olmadı.</p>`;
            }
        }

        function setCarrierPanelFilter(filter) {
            carrierPanelFilter = filter;
            document.getElementById("filterPillAll").classList.toggle("active", filter === 'all');
            document.getElementById("filterPillResponded").classList.toggle("active", filter === 'responded');
            document.getElementById("filterPillPending").classList.toggle("active", filter === 'pending');
            renderCarrierPanel();
        }

        function renderCarrierPanel() {
            const list = document.getElementById("carriersPanelList");
            const searchEl = document.getElementById("carrierPanelSearch");
            const query = (searchEl ? searchEl.value : "").toLowerCase().trim();

            const respondedCount = detailCarriersCache.filter(c => c.has_submitted).length;
            const pendingCount = detailCarriersCache.filter(c => !c.has_submitted).length;
            document.getElementById("tabAllCount").textContent = detailCarriersCache.length;
            document.getElementById("tabRespondedCount").textContent = respondedCount;
            document.getElementById("tabPendingCount").textContent = pendingCount;

            let filtered = detailCarriersCache.filter(c => {
                if (carrierPanelFilter === 'responded' && !c.has_submitted) return false;
                if (carrierPanelFilter === 'pending' && c.has_submitted) return false;
                if (query) {
                    const name = (c.company_name || "").toLowerCase();
                    const email = (c.email || "").toLowerCase();
                    if (!name.includes(query) && !email.includes(query)) return false;
                }
                return true;
            });

            if (filtered.length === 0) {
                list.innerHTML = `<div class="text-center text-muted small p-4"><i class="bi bi-people fs-3 d-block mb-2 opacity-50"></i>Uyğun daşıyıcı tapılmadı.</div>`;
                return;
            }

            let html = "";
            filtered.forEach((c, idx) => {
                const color = AVATAR_PALETTE[idx % AVATAR_PALETTE.length];
                const initials = getInitials(c.company_name);

                let deliveryBadge;
                if (c.mail_status === 'delivered') {
                    deliveryBadge = `<span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25">Çatdırıldı</span>`;
                } else if (c.mail_status === 'failed') {
                    deliveryBadge = `<span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25">Çatdırılmadı</span>`;
                } else {
                    deliveryBadge = `<span class="badge bg-secondary bg-opacity-10 text-secondary border border-secondary border-opacity-25">Göndərilir...</span>`;
                }

                let quoteStatus = c.has_submitted
                    ? `<span class="text-success fw-bold" style="font-size: 11.5px;"><i class="bi bi-check-circle-fill me-1"></i>Təklif alındı</span>`
                    : `<span class="text-warning fw-bold" style="font-size: 11.5px;"><i class="bi bi-hourglass-split me-1"></i>Təklif yoxdur</span>`;

                let actionBtn;
                if (c.mail_status === 'failed') {
                    actionBtn = `<button class="btn btn-sm btn-outline-primary rounded-pill px-2 py-1" style="font-size: 11px;" onclick="resendCarrierEmail(${c.quote_id})"><i class="bi bi-arrow-clockwise me-1"></i>Yenidən göndər</button>`;
                } else if (!c.has_submitted) {
                    actionBtn = `<button class="btn btn-sm btn-outline-secondary rounded-pill px-2 py-1" style="font-size: 11px;" onclick="sendSingleReminder(${c.quote_id})"><i class="bi bi-bell me-1"></i>Reminder göndər</button>`;
                } else {
                    actionBtn = "";
                }

                const checkbox = !c.has_submitted
                    ? `<input type="checkbox" class="form-check-input flex-shrink-0" style="margin-top:2px;" ${selectedReminderIds.has(c.quote_id) ? 'checked' : ''} onchange="toggleReminderSelect(${c.quote_id}, this.checked)">`
                    : `<span style="width:1.15em; display:inline-block;"></span>`;

                html += `
                    <div class="carrier-panel-row d-flex align-items-start gap-2">
                        ${checkbox}
                        <div class="avatar-circle" style="background:${color};">${initials}</div>
                        <div class="flex-grow-1" style="min-width:0;">
                            <div class="d-flex justify-content-between align-items-start gap-2 flex-wrap">
                                <div style="min-width:0;">
                                    <div class="fw-bold text-dark text-truncate" style="font-size: 13px; max-width: 170px;">${c.company_name || 'Daşıyıcı'}</div>
                                    <div class="text-muted text-truncate" style="font-size: 11.5px; max-width: 170px;">${c.email || ''}</div>
                                </div>
                                ${deliveryBadge}
                            </div>
                            <div class="d-flex justify-content-between align-items-center mt-2 flex-wrap gap-1">
                                ${quoteStatus}
                                ${actionBtn}
                            </div>
                        </div>
                    </div>
                `;
            });

            list.innerHTML = html;
        }

        function updateSelectedReminderCount() {
            const n = selectedReminderIds.size;
            const el1 = document.getElementById("detailSelectedCount");
            const el2 = document.getElementById("panelSelectedCount");
            if (el1) el1.textContent = n;
            if (el2) el2.textContent = n;
        }

        function toggleReminderSelect(quoteId, checked) {
            if (checked) selectedReminderIds.add(quoteId);
            else selectedReminderIds.delete(quoteId);
            updateSelectedReminderCount();
        }

        function selectAllPendingReminders() {
            detailCarriersCache.filter(c => !c.has_submitted).forEach(c => selectedReminderIds.add(c.quote_id));
            renderCarrierPanel();
            updateSelectedReminderCount();
        }

        function clearAllReminderSelection() {
            selectedReminderIds.clear();
            renderCarrierPanel();
            updateSelectedReminderCount();
        }

        async function sendSingleReminder(quoteId) {
            try {
                const res = await fetch(`/quotes/reminder/${quoteId}`, { method: "POST" });
                const data = await res.json();
                if (res.ok) {
                    alert(data.message || "Reminder göndərildi!");
                    if (currentDetailRequestId) loadDetailCarriersStatus(currentDetailRequestId);
                } else {
                    alert("Xəta: " + formatErrorDetail(data.detail));
                }
            } catch (err) {
                alert("Server xətası!");
            }
        }

        async function resendCarrierEmail(quoteId) {
            try {
                const res = await fetch(`/quotes/resend/${quoteId}`, { method: "POST" });
                const data = await res.json();
                if (res.ok) {
                    alert(data.message || "Mail yenidən göndərildi!");
                    if (currentDetailRequestId) loadDetailCarriersStatus(currentDetailRequestId);
                } else {
                    alert("Xəta: " + formatErrorDetail(data.detail));
                }
            } catch (err) {
                alert("Server xətası!");
            }
        }

        async function sendSelectedReminders() {
            const ids = Array.from(selectedReminderIds);
            if (ids.length === 0) {
                alert("Zəhmət olmasa Daşıyıcılar panelindən azı bir daşıyıcı seçin.");
                return;
            }
            try {
                const res = await fetch(`/quotes/reminder-batch`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ quote_ids: ids })
                });
                const data = await res.json();
                if (res.ok) {
                    alert(data.message || "Reminderlər göndərildi!");
                    if (currentDetailRequestId) loadDetailCarriersStatus(currentDetailRequestId);
                } else {
                    alert("Xəta: " + formatErrorDetail(data.detail));
                }
            } catch (err) {
                alert("Server xətası!");
            }
        }
    </script>
</body>
</html>
