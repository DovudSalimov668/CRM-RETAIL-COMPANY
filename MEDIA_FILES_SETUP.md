# Media Files Setup - Complete Guide

## ✅ Current Status

**Media folder structure is now set up!**

### Folder Structure Created:
```
media/
├── profiles/          # Customer profile images
│   └── .gitkeep      # Preserves folder in git
└── products/         # Product images
    └── .gitkeep      # Preserves folder in git
```

## 📋 Configuration Summary

### 1. **Django Settings** ✅
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```
- ✅ Configured in `retail_crm/settings.py`

### 2. **URL Configuration** ✅
```python
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
- ✅ Configured in `retail_crm/urls.py`
- ✅ Works in both development and production

### 3. **Model Configuration** ✅

**Customer Profile Images:**
```python
profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
```
- ✅ Saves to: `media/profiles/`
- ✅ Used in: Customer model

**Product Images:**
```python
image = models.ImageField(upload_to='products/', null=True, blank=True)
```
- ✅ Saves to: `media/products/`
- ✅ Used in: Product model

### 4. **Git Configuration** ✅
- ✅ `.gitignore` includes `media/` folder
- ✅ `.gitkeep` files preserve folder structure

## 🚀 How It Works

### Uploading Images:

1. **Customer Profile Image:**
   - User uploads image via form
   - Django saves to: `media/profiles/filename.jpg`
   - URL: `/media/profiles/filename.jpg`

2. **Product Image:**
   - Admin/staff uploads image via form
   - Django saves to: `media/products/filename.jpg`
   - URL: `/media/products/filename.jpg`

### Accessing Images:

**In Templates:**
```django
{% if customer.profile_image %}
    <img src="{{ customer.profile_image.url }}" alt="Profile">
{% endif %}

{% if product.image %}
    <img src="{{ product.image.url }}" alt="{{ product.name }}">
{% endif %}
```

**In Code:**
```python
customer.profile_image.url  # Returns: /media/profiles/filename.jpg
product.image.url            # Returns: /media/products/filename.jpg
```

## 📁 File Storage Locations

### Local Development:
- **Path:** `C:\Users\User\Desktop\CRM\media\`
- **Profiles:** `media/profiles/`
- **Products:** `media/products/`

### Production (Render.com):
- **Path:** `/app/media/` (on Render server)
- **Profiles:** `/app/media/profiles/`
- **Products:** `/app/media/products/`

## ⚠️ Important Notes

### For Production (Render.com):

**Current Setup:**
- ✅ Media files are served through Django
- ✅ Works for small deployments
- ⚠️ Files are stored on the server (not persistent across deployments)

**Recommended for Production:**
- Use cloud storage (AWS S3, Cloudinary, etc.)
- Files persist across deployments
- Better performance and scalability
- Free tiers available

### File Size Limits:

**Django Default:**
- No built-in file size limit
- Server may have limits (Render: varies by plan)

**Recommended:**
- Profile images: Max 2-5 MB
- Product images: Max 5-10 MB
- Add validation in forms if needed

## 🔧 Testing Media Upload

### Test Profile Image Upload:

1. Go to: `/customers/new/` or `/customers/<id>/edit/`
2. Upload a profile image
3. Check: `media/profiles/` folder
4. Verify image displays on customer detail page

### Test Product Image Upload:

1. Go to: `/products/new/` or `/products/<id>/edit/`
2. Upload a product image
3. Check: `media/products/` folder
4. Verify image displays on product page

## 📝 File Permissions

### Local Development:
- ✅ No special permissions needed
- ✅ Django creates folders automatically

### Production (Render.com):
- ✅ Folders created automatically
- ✅ Permissions handled by Django
- ✅ No manual setup needed

## 🗑️ Cleaning Up Old Images

**Manual Cleanup:**
```bash
# Remove unused profile images (be careful!)
# Django doesn't auto-delete when model is deleted
```

**Automatic Cleanup (Optional):**
- Use Django signals to delete files when model is deleted
- Or use a management command to clean orphaned files

## ✅ Verification Checklist

- [x] Media folder created
- [x] Profiles subfolder created
- [x] Products subfolder created
- [x] .gitkeep files added
- [x] Settings configured (MEDIA_URL, MEDIA_ROOT)
- [x] URLs configured for media serving
- [x] Models use correct upload_to paths
- [x] .gitignore includes media folder

## 🎯 Summary

**Everything is set up correctly!**

- ✅ Media folder structure created
- ✅ Django settings configured
- ✅ URLs configured for serving media
- ✅ Models configured for image uploads
- ✅ Ready for development and production

**Next Steps:**
1. Test uploading a profile image
2. Test uploading a product image
3. Verify images display correctly
4. For production, consider cloud storage for better reliability

---

**Note:** Media files in `media/` folder are ignored by git (as per `.gitignore`). This is correct - you don't want to commit user-uploaded files to git!

