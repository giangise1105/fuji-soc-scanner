# SOC Scanner PWA

PWA quét QR/barcode mã SOC, lưu local (IndexedDB), export CSV. Chạy 100% offline sau lần load đầu.

## Deploy lên GitHub Pages (5 bước)

1. Tạo repo mới trên GitHub (ví dụ: `soc-scanner`)
2. Upload 3 files: `index.html`, `manifest.json`, `sw.js`
3. Vào **Settings → Pages**
4. Source: chọn branch `main`, folder `/` (root) → Save
5. Sau 1–2 phút, URL `https://<username>.github.io/<repo>/` sẽ live

## Add to Home Screen

### iPhone/iPad (Safari, iOS 16.4+)
1. Mở URL trong **Safari** (không phải Chrome)
2. Bấm nút **Share** (□↑) ở thanh dưới
3. Cuộn xuống → **Add to Home Screen**
4. Đặt tên → **Add**

### Android (Chrome 100+)
1. Mở URL trong **Chrome**
2. Menu **⋮** → **Install app** (hoặc **Add to Home Screen**)
3. **Install**

## Sử dụng

| Tab | Chức năng |
|-----|-----------|
| 📷 Quét | Bấm "Bắt đầu quét" → chĩa camera vào QR/barcode SOC → nhập số lượng → Lưu |
| 📋 Lịch sử | Xem records, tìm kiếm, xóa từng dòng, export CSV |
| ⚙️ Cài đặt | Export tất cả, xóa toàn bộ, hướng dẫn cài đặt |

## PDA Scanner Support

App tự động nhận input từ PDA hardware scanner (HID keyboard mode):
- Bấm scan trên PDA → app nhận chuỗi → form mở tự động
- Không cần mode switch, không cần focus input
- Camera và PDA hoạt động song song
- Auto-stop camera khi PDA scan thành công

**Yêu cầu PDA:** scanner cấu hình HID Keyboard mode, suffix Enter (mặc định).

## Format SOC

Regex: `^\d-\d{7,8}-\d{3}$`
Ví dụ: `1-1234567-001`, `1-12345678-002`

## Offline

Lần đầu cần internet để load app + cache libs (~500KB).
Sau đó chạy hoàn toàn offline qua Service Worker.

## Tech

- Vanilla JS, không framework, không build step
- [html5-qrcode](https://github.com/mebjas/html5-qrcode) — quét QR/barcode
- [Dexie.js](https://dexie.org) — IndexedDB wrapper
- Service Worker cache-first — offline PWA
- Không backend, không tracking, không đăng nhập

## Generate icons tốt hơn

Để có icon với chữ "SOC", chạy lệnh này trong DevTools Console (sau khi app đang chạy):

```js
function genIcon(size) {
  const c=document.createElement('canvas'); c.width=c.height=size;
  const x=c.getContext('2d');
  x.fillStyle='#0a0a0a'; x.fillRect(0,0,size,size);
  x.fillStyle='#ff6b35'; x.font='bold '+Math.round(size*.35)+'px sans-serif';
  x.textAlign='center'; x.textBaseline='middle';
  x.fillText('SOC',size/2,size/2);
  return c.toDataURL('image/png');
}
console.log('192:', genIcon(192));
console.log('512:', genIcon(512));
```

Copy base64 strings và paste vào `manifest.json` icons.src + `<link rel="apple-touch-icon">` trong `index.html`.
