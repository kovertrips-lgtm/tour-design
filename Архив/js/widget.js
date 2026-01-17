const utilsScriptUrl = "https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js";
(function () {
    let TOUR_SETTINGS = { tourName: "Клиновец", tourId: "klinovec_general", tourDate: "TBD", tourType: "oneday", telegramLink: "https://t.me/kover_trip", priceFull: 1190, priceDeposit: 500 };
    let SYSTEM_CONFIG = { webhook: "https://hook.eu2.make.com/t118j4fcirfp3s6srdt97ahsr9hggo63", stripePublicKey: "pk_live_51SE6PPDcw9kAY89HfWvBpSfQqQ4BvbF5D9cEOkQ1DC5YNK5HARwuhhWZzTEQA6WCoATixBmkEJ8eTbpVUyw96wK0001cNUyYD6", priceSeat: 100 };

    function parseConfig() {
        const d = document.querySelector('.t-text');
        if (d) {
            const t = d.innerText || d.textContent;
            t.split('\n').forEach(l => {
                const [k, v] = l.split(':').map(s => s.trim());
                if (k && v) {
                    if (k === 'WEBHOOK') SYSTEM_CONFIG.webhook = v;
                    if (k === 'NAME') TOUR_SETTINGS.tourName = v;
                    if (k === 'PRICE_FULL') TOUR_SETTINGS.priceFull = parseInt(v);
                    if (k === 'PRICE_DEPOSIT') TOUR_SETTINGS.priceDeposit = parseInt(v);
                    if (k === 'PRICE_SEAT') SYSTEM_CONFIG.priceSeat = parseInt(v);
                }
            });
        }
    }

    let state = { count: 1, payType: 'full', step: 1 };
    let stripe = null, checkout = null, iti = null;

    function ensureModal() {
        if (!document.getElementById('booking-modal-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'booking-modal-overlay';
            overlay.className = 'modal-overlay';
            overlay.setAttribute('onmousedown', 'handleOverlayMouseDown(event)');
            overlay.setAttribute('onclick', 'handleOverlayClick(event)');
            overlay.innerHTML = `<div class="modal-close-btn" onclick="closeBookingModal()">✕</div><div id="booking-widget-root"><div class="b-loading">Загрузка...</div></div>`;
            document.body.appendChild(overlay);
        } else {
            const existingRoot = document.getElementById('booking-widget-root');
            const overlay = document.getElementById('booking-modal-overlay');
            if (existingRoot && !overlay.contains(existingRoot)) overlay.appendChild(existingRoot);
        }
    }

    function init() { parseConfig(); try { stripe = Stripe(SYSTEM_CONFIG.stripePublicKey); } catch (e) { console.error(e); } render(); }

    function render() {
        const root = document.getElementById('booking-widget-root'); if (!root) return;
        root.innerHTML = `
        <div class="b-container" onclick="event.stopPropagation()">
            <div class="b-card active" id="card-step-1">
                <div class="b-card-header" id="header-1"><div class="b-card-title">1. Параметры поездки</div><div class="b-card-status" id="status-1">Изменить</div></div>
                <div class="b-card-body">
                    <div class="b-plans-grid">
                        <div class="b-plan-card selected" id="plan-full"><div class="b-left-part"><div class="b-radio-circle"></div><div class="b-plan-info"><div class="b-plan-title">Оплатить полностью</div><div class="b-plan-desc">Без доплат в&nbsp;будущем</div></div></div><div class="b-plan-price">${TOUR_SETTINGS.priceFull} Kč</div></div>
                        <div class="b-plan-card" id="plan-depo"><div class="b-left-part"><div class="b-radio-circle"></div><div class="b-plan-info"><div class="b-plan-title">Внести залог</div><div class="b-plan-desc">Остаток <span class="b-remainder-amount" id="lbl-remainder">${TOUR_SETTINGS.priceFull - TOUR_SETTINGS.priceDeposit} Kč</span> за&nbsp;10 дней до&nbsp;тура</div></div></div><div class="b-plan-price">${TOUR_SETTINGS.priceDeposit} Kč</div></div>
                    </div>
                    <div class="b-row"><div class="b-label">Участники</div><div class="b-stepper"><div class="b-step-btn" id="btn-minus">–</div><div class="b-step-val" id="val-cnt">1</div><div class="b-step-btn" id="btn-plus">+</div></div></div>
                    <div class="b-receipt" id="receipt-1"></div>
                    <button class="b-btn" id="btn-next">Далее</button>
                </div>
            </div>
            <div class="b-card locked" id="card-step-2">
                <div id="card-loader" class="b-spinner-overlay"><div class="b-spinner"></div></div>
                <div class="b-card-header"><div class="b-card-title">2. Данные участников</div></div>
                <div class="b-card-body">
                    <div id="passengers-list"></div>
                    <div style="margin-top: 30px; border-top: 1px solid var(--border-light); padding-top: 20px;">
                        <div class="b-input-group" style="margin-top: 12px; margin-bottom: 0;">
                            <div class="b-consent-wrapper">
                                <input type="checkbox" id="chk-consent" class="b-checkbox">
                                <label for="chk-consent" class="b-consent-label">Я даю <span class="b-link" onclick="openPrivacyModal(event)">согласие на обработку персональных данных</span></label>
                            </div>
                        </div>
                    </div>
                    <div class="b-receipt" id="receipt-2"></div>
                    <button class="b-btn" id="btn-pay">Оплатить</button>
                </div>
            </div>
        </div>
        <div class="b-payment-overlay" id="payment-overlay">
            <div class="b-payment-modal"><div class="b-close-cross" id="btn-close-pay">✕</div><h3 style="margin:0 0 20px 0; font-size:22px;">Оплата картой</h3><div id="stripe-box"></div></div>
        </div>
        <div class="b-payment-overlay" id="privacy-overlay" style="z-index: 2147483645;" onclick="closePrivacyModal(); event.stopPropagation()">
            <div class="b-payment-modal" style="max-width: 600px;" onclick="event.stopPropagation()"><div class="b-close-cross" onclick="closePrivacyModal(); event.stopPropagation()">✕</div><h3 style="margin:0 0 20px 0; font-size:20px;">Zpracování osobních údajů</h3><div style="font-size: 14px; line-height: 1.6; color: #333;"><p><strong>1. Správce osobních údajů</strong><br>Správcem vašich osobních údajů je společnost Kover Travel s.r.o.</p><p><strong>2. Účel zpracování</strong><br>Vaše osobní údaje zpracováváme za účelem:<br>- Vyřízení vaší objednávky a poskytnutí služeb.<br>- Komunikace týkající se vaší rezervace.<br>- Plnění zákonných povinností (např. účetnictví).</p></div></div>
        </div>`;
        bindEvents(); updateUI();
    }

    function bindEvents() {
        document.getElementById('plan-full').addEventListener('click', () => setPlan('full'));
        document.getElementById('plan-depo').addEventListener('click', () => setPlan('deposit'));
        document.getElementById('header-1').onclick = () => goToStep(1);
        document.getElementById('btn-minus').onclick = () => changeCount(-1);
        document.getElementById('btn-plus').onclick = () => changeCount(1);
        document.getElementById('btn-next').onclick = toStep2;
        document.getElementById('btn-pay').onclick = pay;
        document.getElementById('btn-close-pay').onclick = closePay;
        const c = document.getElementById('chk-consent'); if (c) c.addEventListener('change', checkReadiness);
    }

    function setPlan(t) { state.payType = t; updateUI(); document.getElementById('plan-full').classList.toggle('selected', t === 'full'); document.getElementById('plan-depo').classList.toggle('selected', t === 'deposit'); }
    function goToStep(s) { if (s === 1) { const c1 = document.getElementById('card-step-1'), c2 = document.getElementById('card-step-2'); c1.classList.remove('done', 'locked'); c1.classList.add('active'); c2.classList.remove('active'); c2.classList.add('locked'); } }

    function initPhoneLogic() {
        const ph = document.getElementById('inp-phone'); if (!ph) { iti = null; return; }
        const errM = document.querySelector("#error-msg"), valM = document.querySelector("#valid-msg");
        const reset = () => { ph.classList.remove("error"); if (errM) { errM.innerHTML = ""; errM.style.display = "none"; } if (valM) valM.style.display = "none"; };
        if (window.intlTelInput) {
            if (iti) iti.destroy();
            iti = window.intlTelInput(ph, { utilsScript: utilsScriptUrl, initialCountry: "cz", preferredCountries: ["cz", "ua", "ru", "at", "de", "pl"], separateDialCode: true, autoPlaceholder: "aggressive" });
            ph.addEventListener('blur', () => { reset(); if (ph.value.trim()) { if (iti.isValidNumber()) { if (valM) valM.style.display = "block"; } else { ph.classList.add("error"); if (errM) { errM.innerHTML = "Неверный номер"; errM.style.display = "block"; } } } checkReadiness(); });
            ph.addEventListener('change', reset); ph.addEventListener('keyup', reset); ph.addEventListener('countrychange', () => { reset(); checkReadiness(); });
        }
        ph.addEventListener('input', checkReadiness);
    }

    function toStep2() {
        document.getElementById('card-step-1').classList.remove('active'); document.getElementById('card-step-1').classList.add('done'); document.getElementById('status-1').innerText = `${state.count} чел • ${state.payType === 'full' ? 'Полная' : 'Залог'}`;
        const c2 = document.getElementById('card-step-2'); c2.classList.remove('locked'); c2.classList.add('active');
        const list = document.getElementById('passengers-list'); list.innerHTML = '';
        for (let i = 0; i < state.count; i++) {
            let cf = ''; if (i === 0) cf = `<div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border-light);"><div class="b-input-label" style="font-weight:600;color:var(--text-main);margin-bottom:10px;">Контактные данные</div><div class="b-input-group"><input type="email" class="b-input" id="inp-email" placeholder="Email" name="email"><div id="err-email" class="msg error">Email некорректен</div></div><div class="b-input-group" style="margin-bottom:0;"><input type="tel" class="b-input" id="inp-phone"><span id="valid-msg" class="msg valid">✓ OK</span><span id="error-msg" class="msg error"></span></div></div>`;
            const g = document.createElement('div'); g.className = 'b-passenger-group';
            g.innerHTML = `<div class="b-passenger-title">Участник ${i + 1}</div><div class="b-input-row"><div class="b-input-group"><input type="text" class="b-input pass-firstname" placeholder="Имя"><div class="b-latin-error">Latina only</div></div><div class="b-input-group"><input type="text" class="b-input pass-lastname" placeholder="Фамилия"><div class="b-latin-error">Latina only</div></div></div><div class="b-input-group" style="margin-bottom:0;"><input type="text" class="b-input pass-dob flatpickr-input" placeholder="ДД.ММ.ГГГГ" autocomplete="off"><div class="b-age-warning" id="warn-young-${i}">До 7 лет нужен запрос</div><div class="b-age-warning" id="warn-old-${i}">62+ нужен запрос</div><div class="b-year-error" id="err-year-${i}">Проверьте год</div></div>${cf}`;
            list.appendChild(g);
        }
        initPhoneLogic();
        const em = document.getElementById('inp-email'); if (em) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            em.addEventListener('blur', () => { if (em.value.trim().length > 0 && !re.test(em.value.trim())) em.classList.add('error'); else em.classList.remove('error'); checkReadiness(); });
            em.addEventListener('input', checkReadiness);
        }
        document.querySelectorAll('.pass-firstname, .pass-lastname').forEach(el => {
            el.addEventListener('input', function () {
                const v = this.value, c = v.replace(/[^a-zA-Z\s-]/g, '');
                if (v !== c) { this.value = c; this.classList.add('shake-field'); setTimeout(() => this.classList.remove('shake-field'), 400); const err = this.parentNode.querySelector('.b-latin-error'); if (err) { err.classList.add('visible'); setTimeout(() => err.classList.remove('visible'), 3000); } }
                checkReadiness();
            });
            el.addEventListener('blur', function () { if (this.value.length > 0) this.value = this.value.charAt(0).toUpperCase() + this.value.slice(1).toLowerCase(); checkReadiness(); });
        });
        document.querySelectorAll('.pass-dob').forEach((d, idx) => initValidations(idx, d, d.parentNode));
        checkReadiness();
        const ov = document.getElementById('booking-modal-overlay'); if (ov) ov.scrollTop = 0;
    }

    function initValidations(idx, el, p) {
        if (typeof flatpickr !== 'undefined') flatpickr(el, { dateFormat: "d.m.Y", maxDate: "today", disableMobile: "true", locale: "ru", yearSelectorType: "dropdown", appendTo: p, static: true, onChange: function (sd) { validateAge(sd[0], idx); validateYear(sd[0], idx, el); checkReadiness(); }, onReady: function (d, s, f) { if (!f.selectedDates.length) f.jumpToDate("01.01.2000") } });
        el.addEventListener('input', checkReadiness);
    }

    function validateAge(d, i) { if (!d) return; const a = Math.abs(new Date(new Date() - d).getUTCFullYear() - 1970); const y = d.getFullYear(); if (y > 1920) { document.getElementById(`warn-young-${i}`).classList.toggle('visible', a < 7); document.getElementById(`warn-old-${i}`).classList.toggle('visible', a > 62); } }
    function validateYear(d, i, el) { if (!d && el.value.length > 0) el.classList.add('error'); else if (d && d.getFullYear() < 1920) el.classList.add('error'); else el.classList.remove('error'); }

    function checkReadiness() {
        const btn = document.getElementById('btn-pay'), em = document.getElementById('inp-email'), ph = document.getElementById('inp-phone');
        if (!btn || !em || !ph) { if (btn) { btn.classList.add('is-locked'); btn.classList.remove('is-ready'); } return; }
        let ok = true; document.querySelectorAll('.b-passenger-group').forEach(g => { if (g.querySelector('.pass-firstname').value.length < 2 || g.querySelector('.pass-lastname').value.length < 2 || !g.querySelector('.pass-dob').value) ok = false; });
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em.value.trim())) ok = false;
        let phOk = false; if (window.iti && typeof window.iti.isValidNumber === 'function') phOk = window.iti.isValidNumber(); else phOk = ph.value.length >= 5; if (!phOk) ok = false;
        if (!document.getElementById('chk-consent').checked) ok = false;
        const tot = (state.payType === 'full' ? TOUR_SETTINGS.priceFull : TOUR_SETTINGS.priceDeposit) * state.count;
        if (btn.innerText !== "Загрузка...") btn.innerText = `Оплатить ${tot} Kč`;
        if (ok) { btn.classList.remove('is-locked'); btn.classList.add('is-ready'); } else { btn.classList.add('is-locked'); btn.classList.remove('is-ready'); }
    }

    function changeCount(d) { if (state.count + d >= 1 && state.count + d <= 10) { state.count += d; updateUI(); } }
    function updateUI() {
        const isF = state.payType === 'full', base = isF ? TOUR_SETTINGS.priceFull : TOUR_SETTINGS.priceDeposit, tot = base * state.count;
        document.getElementById('val-cnt').innerText = state.count;
        document.getElementById('lbl-remainder').innerText = (TOUR_SETTINGS.priceFull - TOUR_SETTINGS.priceDeposit) + " Kč";
        const h = `<div class="b-receipt-row"><span>${state.count} x ${isF ? 'Билет' : 'Залог'}</span><span>${tot} Kč</span></div><div class="b-receipt-divider"></div><div class="b-receipt-total"><span>Итого</span><span>${tot} Kč</span></div>`;
        document.getElementById('receipt-1').innerHTML = h; document.getElementById('receipt-2').innerHTML = h;
        document.getElementById('btn-next').disabled = false; document.getElementById('btn-pay').innerText = `Оплатить ${tot} Kč`;
    }
    function closePay() {
        document.getElementById('payment-overlay').classList.remove('show');
        if (checkout) { try { checkout.destroy() } catch (e) { } checkout = null; }
        document.getElementById('stripe-box').innerHTML = '';
        document.getElementById('btn-pay').disabled = false;
        document.getElementById('btn-pay').innerText = "Оплатить";
    }

    function getDeviceType() {
        const ua = navigator.userAgent;
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) return "Tablet";
        if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated/.test(ua)) return "Mobile";
        return "Desktop";
    }

    async function pay() {
        const btn = document.getElementById('btn-pay');
        if (btn.classList.contains('is-locked')) { const e = document.querySelector('.b-card.active .error'); if (e) { e.scrollIntoView({ behavior: 'smooth', block: 'center' }); e.classList.add('shake-field'); setTimeout(() => e.classList.remove('shake-field'), 400); } return; }
        document.getElementById('card-loader').classList.add('visible'); btn.disabled = true;
        const pass = []; document.querySelectorAll('.b-passenger-group').forEach((g, i) => { pass.push({ firstname: g.querySelector('.pass-firstname').value, lastname: g.querySelector('.pass-lastname').value, dob: g.querySelector('.pass-dob').value }); });
        const em = document.getElementById('inp-email').value, ph = iti ? iti.getNumber() : document.getElementById('inp-phone').value;
        const isF = state.payType === 'full', tot = (isF ? TOUR_SETTINGS.priceFull : TOUR_SETTINGS.priceDeposit) * state.count, rem = isF ? 0 : (TOUR_SETTINGS.priceFull - TOUR_SETTINGS.priceDeposit) * state.count;

        const payload = {
            timestamp: new Date().toLocaleString("ru-RU", { timeZone: "Europe/Prague" }),
            device_type: getDeviceType(),
            tour_name: TOUR_SETTINGS.tourName,
            tour_id: TOUR_SETTINGS.tourId,
            tour_date: TOUR_SETTINGS.tourDate,
            tour_type: TOUR_SETTINGS.tourType,
            telegram_link: TOUR_SETTINGS.telegramLink,
            passenger_count: state.count,
            selected_seats: "Без выбора мест",
            payment_type: isF ? 'Полная оплата' : 'Залог',
            currency: "CZK",
            locale: "ru",
            total_pay_now: tot,
            remaining_balance: rem,
            total_order_value: TOUR_SETTINGS.priceFull * state.count,
            seats_surcharge: 0,
            buyer_email: em,
            buyer_phone: ph,
            productName: TOUR_SETTINGS.tourName
        };

        // --- PASSENGERS (SPLIT NAME UPDATE) ---
        pass.forEach((p, i) => {
            payload[`passenger_${i + 1}_firstname`] = p.firstname;
            payload[`passenger_${i + 1}_lastname`] = p.lastname;
            // Keep full name for backward compatibility/readability
            payload[`passenger_${i + 1}_name`] = `${p.firstname} ${p.lastname}`;
            payload[`passenger_${i + 1}_dob`] = p.dob;
        });

        payload.all_passengers_summary = pass.map(p => `${p.firstname} ${p.lastname}`).join(', ');

        try {
            const r = await fetch(SYSTEM_CONFIG.webhook, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
            const d = await r.json(); if (!d.clientSecret) throw new Error("Make error");
            const ov = document.getElementById('booking-modal-overlay'); if (ov) ov.scrollTop = 0;
            document.getElementById('payment-overlay').classList.add('show'); document.getElementById('card-loader').classList.remove('visible');
            checkout = await stripe.initEmbeddedCheckout({ clientSecret: d.clientSecret }); checkout.mount('#stripe-box');
        } catch (e) { console.error(e); alert("Ошибка: " + e.message); document.getElementById('card-loader').classList.remove('visible'); btn.disabled = false; }
    }

    /* PRIVACY MODAL LOGIC (ADDED) */
    window.openPrivacyModal = function (e) {
        e.preventDefault(); e.stopPropagation();
        var o = document.getElementById('privacy-overlay');
        if (o) o.classList.add('show');
    }
    window.closePrivacyModal = function () {
        var o = document.getElementById('privacy-overlay');
        if (o) o.classList.remove('show');
    }

    setTimeout(() => { ensureModal(); init(); }, 1000);
})();

// GLOBAL TRIGGERS
window.openBookingModal = function () {
    const o = document.getElementById('booking-modal-overlay');
    if (o) {
        o.classList.add('active');
        document.body.classList.add('modal-open');
    } else console.warn("Modal not init");
}
window.closeBookingModal = function () {
    const o = document.getElementById('booking-modal-overlay');
    if (o) {
        o.classList.remove('active');
        document.body.classList.remove('modal-open');
    }
}
let omt = null; window.handleOverlayMouseDown = function (e) { omt = e.target; }
window.handleOverlayClick = function (e) { if (e.target === e.currentTarget && omt === e.currentTarget) closeBookingModal(); omt = null; }
document.addEventListener('click', function (e) { const t = e.target.closest('a[href="#book-now"], .js-open-booking'); if (t) { e.preventDefault(); openBookingModal(); } });
