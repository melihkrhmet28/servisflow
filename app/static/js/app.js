/**
 * ServisFlow - İstemci Tarafı Form ve Durum Yönetimi
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("service-request-form");
  const submitButton = document.getElementById("submit-button");
  const buttonSpinner = document.getElementById("button-spinner");
  const buttonText = document.getElementById("button-text");

  // Bildirim alanları
  const errorAlert = document.getElementById("form-error-alert");
  const errorTitle = document.getElementById("error-title");
  const errorDetails = document.getElementById("error-details");
  const successCard = document.getElementById("form-success-card");
  const successSummary = document.getElementById("success-summary");
  const resetFormBtn = document.getElementById("btn-reset-form");

  // Form elemanları
  const fullNameInput = document.getElementById("full_name");
  const emailInput = document.getElementById("email");
  const serviceTypeSelect = document.getElementById("service_type");
  const messageInput = document.getElementById("message");
  const charCounter = document.getElementById("char-counter");

  // İzin verilen hizmet türleri
  const VALID_SERVICE_TYPES = [
    "randevu_yonetimi",
    "musteri_bildirim",
    "ozel_entegrasyon",
  ];

  const SERVICE_LABELS = {
    randevu_yonetimi: "Akıllı Randevu Yönetimi",
    musteri_bildirim: "Müşteri Bildirim & Hatırlatma",
    ozel_entegrasyon: "Özel Entegrasyon & Kurumsal Altyapı",
  };

  // Karakter Sayacı Canlı Takip
  if (messageInput && charCounter) {
    messageInput.addEventListener("input", () => {
      const length = messageInput.value.length;
      charCounter.textContent = `${length} / 1000`;
      if (length > 1000) {
        charCounter.classList.add("text-rose-600", "font-bold");
      } else {
        charCounter.classList.remove("text-rose-600", "font-bold");
      }
    });
  }

  // Alan Hata Gösterimi Yardımcısı
  function setFieldError(inputEl, errorElId, message) {
    const errorEl = document.getElementById(errorElId);
    if (!errorEl) return;

    if (message) {
      inputEl.classList.add("border-rose-500", "focus:border-rose-500", "focus:ring-rose-500/20");
      inputEl.classList.remove("border-slate-300", "focus:border-brand-500", "focus:ring-brand-500/20");
      inputEl.setAttribute("aria-invalid", "true");
      errorEl.textContent = message;
      errorEl.classList.remove("hidden");
    } else {
      inputEl.classList.remove("border-rose-500", "focus:border-rose-500", "focus:ring-rose-500/20");
      inputEl.classList.add("border-slate-300", "focus:border-brand-500", "focus:ring-brand-500/20");
      inputEl.removeAttribute("aria-invalid");
      errorEl.textContent = "";
      errorEl.classList.add("hidden");
    }
  }

  // Form Alanlarını Temizle / Sıfırla
  function clearAllErrors() {
    errorAlert.classList.add("hidden");
    errorDetails.innerHTML = "";

    setFieldError(fullNameInput, "full_name_error", null);
    setFieldError(emailInput, "email_error", null);
    setFieldError(serviceTypeSelect, "service_type_error", null);
    setFieldError(messageInput, "message_error", null);
  }

  // E-posta Regex Doğrulayıcı
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // İstemci Doğrulama Mantığı
  function validateForm(data) {
    const errors = {};

    // Ad Soyad Kontrolü
    const trimmedName = (data.full_name || "").trim();
    if (!trimmedName) {
      errors.full_name = "Ad Soyad alanı zorunludur.";
    } else if (trimmedName.length < 2) {
      errors.full_name = "Ad Soyad en az 2 karakter olmalıdır.";
    } else if (trimmedName.length > 100) {
      errors.full_name = "Ad Soyad en fazla 100 karakter olabilir.";
    }

    // E-posta Kontrolü
    const trimmedEmail = (data.email || "").trim();
    if (!trimmedEmail) {
      errors.email = "E-posta alanı zorunludur.";
    } else if (!isValidEmail(trimmedEmail)) {
      errors.email = "Lütfen geçerli bir e-posta adresi giriniz.";
    }

    // Hizmet Türü Kontrolü
    if (!data.service_type || !VALID_SERVICE_TYPES.includes(data.service_type)) {
      errors.service_type = "Lütfen geçerli bir hizmet türü seçiniz.";
    }

    // Mesaj Kontrolü
    const trimmedMessage = (data.message || "").trim();
    if (!trimmedMessage) {
      errors.message = "Talep mesajı alanı zorunludur.";
    } else if (trimmedMessage.length < 10) {
      errors.message = "Talep mesajı en az 10 karakter olmalıdır.";
    } else if (trimmedMessage.length > 1000) {
      errors.message = "Talep mesajı en fazla 1000 karakter olabilir.";
    }

    return errors;
  }

  // Yükleme Durumu Yönetimi
  function setLoadingState(isLoading) {
    if (isLoading) {
      submitButton.disabled = true;
      buttonSpinner.classList.remove("hidden");
      buttonText.textContent = "Gönderiliyor...";
    } else {
      submitButton.disabled = false;
      buttonSpinner.classList.add("hidden");
      buttonText.textContent = "Talebi Gönder";
    }
  }

  // Genel Hata Kutusunu Göster
  function showErrorAlert(title, messageList) {
    errorTitle.textContent = title;
    errorDetails.innerHTML = "";

    if (Array.isArray(messageList) && messageList.length > 0) {
      const ul = document.createElement("ul");
      ul.className = "list-disc list-inside space-y-1 text-xs mt-1";
      messageList.forEach((msg) => {
        const li = document.createElement("li");
        li.textContent = msg;
        ul.appendChild(li);
      });
      errorDetails.appendChild(ul);
    } else if (typeof messageList === "string") {
      errorDetails.textContent = messageList;
    }

    errorAlert.classList.remove("hidden");
    errorAlert.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Anlık Girişlerde Hata Temizleme
  fullNameInput.addEventListener("input", () => setFieldError(fullNameInput, "full_name_error", null));
  emailInput.addEventListener("input", () => setFieldError(emailInput, "email_error", null));
  serviceTypeSelect.addEventListener("change", () => setFieldError(serviceTypeSelect, "service_type_error", null));
  messageInput.addEventListener("input", () => setFieldError(messageInput, "message_error", null));

  // Form Gönderim Dinleyicisi
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAllErrors();

    const formData = {
      full_name: fullNameInput.value.trim(),
      email: emailInput.value.trim(),
      service_type: serviceTypeSelect.value,
      message: messageInput.value.trim(),
    };

    // 1. İstemci Doğrulaması
    const clientErrors = validateForm(formData);
    const hasErrors = Object.keys(clientErrors).length > 0;

    if (hasErrors) {
      const errorMessages = [];
      if (clientErrors.full_name) {
        setFieldError(fullNameInput, "full_name_error", clientErrors.full_name);
        errorMessages.push(clientErrors.full_name);
      }
      if (clientErrors.email) {
        setFieldError(emailInput, "email_error", clientErrors.email);
        errorMessages.push(clientErrors.email);
      }
      if (clientErrors.service_type) {
        setFieldError(serviceTypeSelect, "service_type_error", clientErrors.service_type);
        errorMessages.push(clientErrors.service_type);
      }
      if (clientErrors.message) {
        setFieldError(messageInput, "message_error", clientErrors.message);
        errorMessages.push(clientErrors.message);
      }

      showErrorAlert("Lütfen formdaki eksik veya hatalı alanları düzeltiniz:", errorMessages);
      return;
    }

    // 2. Sunucuya İstek Gönderme
    setLoadingState(true);

    try {
      const response = await fetch("/api/requests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (response.status === 201) {
        // BAŞARILI DURUM: Formu gizle, başarı kartını göster
        form.classList.add("hidden");
        form.reset();
        if (charCounter) charCounter.textContent = "0 / 1000";

        const serviceName = SERVICE_LABELS[result.data.service_type] || result.data.service_type;
        
        successSummary.innerHTML = `
          <div class="grid grid-cols-2 gap-2">
            <div><span class="font-semibold text-slate-700">Talep No:</span> #${result.data.id}</div>
            <div><span class="font-semibold text-slate-700">Ad Soyad:</span> ${escapeHtml(result.data.full_name)}</div>
            <div><span class="font-semibold text-slate-700">E-posta:</span> ${escapeHtml(result.data.email)}</div>
            <div><span class="font-semibold text-slate-700">Hizmet:</span> ${escapeHtml(serviceName)}</div>
          </div>
        `;

        successCard.classList.remove("hidden");
        successCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
      } else if (response.status === 422 || response.status === 400) {
        // DOĞRULAMA HATASI: Sunucudan dönen hata mesajları
        const serverErrors = result.errors || [result.detail || "Doğrulama hatası oluştu."];
        showErrorAlert("Sunucu Doğrulama Hatası:", serverErrors);
      } else {
        // SUNUCU VEYA DİĞER HATA
        showErrorAlert(
          "İşlem Başarısız Oldu",
          result.detail || "Sunucuyla iletişim kurulurken bir hata meydana geldi. Lütfen tekrar deneyiniz."
        );
      }
    } catch (networkError) {
      console.error("Ağ Hatası:", networkError);
      showErrorAlert(
        "Bağlantı Hatası",
        "Sunucuya ulaşılamadı. Lütfen internet bağlantınızı kontrol edip tekrar deneyiniz."
      );
    } finally {
      setLoadingState(false);
    }
  });

  // Yeni Talep Butonuna Basıldığında Formu Yeniden Aç
  if (resetFormBtn) {
    resetFormBtn.addEventListener("click", () => {
      successCard.classList.add("hidden");
      clearAllErrors();
      form.classList.remove("hidden");
      fullNameInput.focus();
    });
  }

  // Güvenlik için HTML Escape Yardımcısı
  function escapeHtml(string) {
    if (!string) return "";
    return String(string)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
