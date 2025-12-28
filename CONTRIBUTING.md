# Ekip Arkadaşları İçin GitHub Kullanım Klavuzu 🛠

Bu proje, düzenli bir çalışma ve çakışmaları önlemek için belirli kurallar çerçevesinde ilerleyecektir. GitHub kullanmayı yeni öğrenen arkadaşlar için temel adımlar aşağıdadır.

## 🌿 Branch (Dal) Yapısı

Projeyi doğrudan `main` branch (ana dal) üzerinde geliştirmeyin. Her yeni özellik veya hata düzeltmesi için yeni bir dal açılmalıdır.

**Branch Naming Format:** `feature/task-name` or `bugfix/issue-name`

Examples:
- `feature/login-page`
- `feature/database-models`
- `bugfix/api-connection-issue`

## 💻 Temel Çalışma Akışı

1. **Create Branch**:
   Ensure your main branch is up to date and create a new branch:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/new-feature-name
   ```

2. **Değişiklikleri Kaydetme (Commit)**:
   Yaptığınız değişiklikleri anlamlı parçalar halinde kaydedin.
   ```bash
   git add .
   git commit -m "Anlamlı ve kısa bir açıklama (örn: Login formu eklendi)"
   ```

3. **Push to Server**:
   Push your work to GitHub:
   ```bash
   git push origin feature/new-feature-name
   ```

4. **Pull Request (PR) Oluşturma**:
   GitHub arayüzüne girin, "Compare & Pull Request" butonuna basın. Ekip arkadaşlarınıza haber verin, inceledikten sonra `main` dalına birleştirilecektir.

## 📝 Commit Mesajı Kuralları

Mesajlarınızın başında ne tür bir değişiklik yaptığınızı belirten etiketler kullanmaya özen gösterin:
- `feat`: Yeni bir özellik eklendiğinde.
- `fix`: Bir hata düzeltildiğinde.
- `docs`: Sadece dökümantasyon değiştiğinde.
- `style`: Kodun işleyişini değiştirmeyen görsel düzenlemeler.
- `refactor`: Kodu düzenleme (hızlandırma, temizleme).

Örnek: `feat: Kullanıcı ulaşım alarm sistemi entegre edildi`

## ⚠️ Dikkat Edilmesi Gerekenler
- **Asla `.env` dosyasını commitlemeyin!** (Zaten `.gitignore` içindedir).
- Başka birinin kodunu değiştirmeden önce mutlaka iletişime geçin.
- Her gün işe başlamadan önce `git pull` yapmayı alışkanlık haline getirin.
