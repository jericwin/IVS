import os

filepath = 'routes/seller.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add upload_to_catbox
search1 = """import uuid
from werkzeug.utils import secure_filename

@seller_bp.route('/seller/sales/update_status/<int:transaction_id>', methods=['POST'])"""

replace1 = """import uuid
from werkzeug.utils import secure_filename
import requests

def upload_to_catbox(file):
    try:
        # Seek to beginning in case it was read before
        file.stream.seek(0)
        files = {'fileToUpload': (file.filename, file.stream, file.mimetype)}
        data = {'reqtype': 'fileupload'}
        resp = requests.post('https://catbox.moe/user/api.php', files=files, data=data, timeout=10)
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception as e:
        print(f"Catbox upload error: {e}")
    return None

@seller_bp.route('/seller/sales/update_status/<int:transaction_id>', methods=['POST'])"""
content = content.replace(search1, replace1)

# 2. update_delivery_status
search2 = """        if file:
            filename = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, unique_filename)
            file.save(filepath)
            
            tx.delivery_evidence_filename = unique_filename
            tx.delivery_status = status"""

replace2 = """        if file:
            catbox_url = upload_to_catbox(file)
            if catbox_url:
                tx.delivery_evidence_filename = catbox_url
            else:
                tx.delivery_evidence_filename = "upload_failed.png"
            tx.delivery_status = status"""
content = content.replace(search2, replace2)

# 3. seller_add_asset part 1
search3 = """        has_main_image = False
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        for i in range(len(variation_names)):
            var_name = variation_names[i]
            var_image = variation_images[i] if i < len(variation_images) else None
            
            var_filename = 'product-1.png'
            if var_image and var_image.filename:
                import uuid
                from werkzeug.utils import secure_filename
                var_filename = str(uuid.uuid4()) + "_" + secure_filename(var_image.filename)
                var_image.save(os.path.join(upload_dir, var_filename))"""

replace3 = """        has_main_image = False
        
        for i in range(len(variation_names)):
            var_name = variation_names[i]
            var_image = variation_images[i] if i < len(variation_images) else None
            
            var_filename = 'product-1.png'
            if var_image and var_image.filename:
                catbox_url = upload_to_catbox(var_image)
                if catbox_url:
                    var_filename = catbox_url"""
content = content.replace(search3, replace3)

# 4. seller_add_asset part 2
search4 = """        if len(variation_names) == 0:
            image = request.files.get('image') # Fallback to old image input if exists
            filename = 'product-1.png'
            if image and image.filename:
                filename = image.filename
                image.save(os.path.join(upload_dir, filename))
                new_asset.image_filename = filename
            new_var = AssetVariation(asset_id=new_asset.id, name="Default", image_filename=filename)
            db.session.add(new_var)"""

replace4 = """        if len(variation_names) == 0:
            image = request.files.get('image') # Fallback to old image input if exists
            filename = 'product-1.png'
            if image and image.filename:
                catbox_url = upload_to_catbox(image)
                if catbox_url:
                    filename = catbox_url
                new_asset.image_filename = filename
            new_var = AssetVariation(asset_id=new_asset.id, name="Default", image_filename=filename)
            db.session.add(new_var)"""
content = content.replace(search4, replace4)

# 5. seller_edit_asset part 1
search5 = """        from models import AssetVariation
        
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        variation_names = request.form.getlist('variation_name[]')
        variation_images = request.files.getlist('variation_image[]')
        existing_variation_ids = request.form.getlist('existing_variation_id[]')
        
        if len(variation_names) > 0:
            # Delete old variations
            AssetVariation.query.filter_by(asset_id=asset.id).delete()
            
            has_main_image = False
            for i in range(len(variation_names)):
                var_name = variation_names[i]
                var_image = variation_images[i] if i < len(variation_images) else None
                
                # Check if there's an existing image to keep
                existing_img = request.form.get(f'existing_image_{i}')
                var_filename = existing_img or 'product-1.png'
                
                if var_image and var_image.filename:
                    import uuid
                    from werkzeug.utils import secure_filename
                    var_filename = str(uuid.uuid4()) + "_" + secure_filename(var_image.filename)
                    var_image.save(os.path.join(upload_dir, var_filename))"""

replace5 = """        from models import AssetVariation
        
        variation_names = request.form.getlist('variation_name[]')
        variation_images = request.files.getlist('variation_image[]')
        existing_variation_ids = request.form.getlist('existing_variation_id[]')
        
        if len(variation_names) > 0:
            # Delete old variations
            AssetVariation.query.filter_by(asset_id=asset.id).delete()
            
            has_main_image = False
            for i in range(len(variation_names)):
                var_name = variation_names[i]
                var_image = variation_images[i] if i < len(variation_images) else None
                
                # Check if there's an existing image to keep
                existing_img = request.form.get(f'existing_image_{i}')
                var_filename = existing_img or 'product-1.png'
                
                if var_image and var_image.filename:
                    catbox_url = upload_to_catbox(var_image)
                    if catbox_url:
                        var_filename = catbox_url"""
content = content.replace(search5, replace5)

# 6. seller_edit_asset part 2
search6 = """        else:
            image = request.files.get('image')
            if image and image.filename:
                filename = image.filename
                image.save(os.path.join(upload_dir, filename))
                asset.image_filename = filename
                
                # Update default variation image if no variations were passed
                default_var = AssetVariation.query.filter_by(asset_id=asset.id).first()
                if default_var:
                    default_var.image_filename = filename
                else:
                    new_var = AssetVariation(asset_id=asset.id, name="Default", image_filename=filename)
                    db.session.add(new_var)"""

replace6 = """        else:
            image = request.files.get('image')
            if image and image.filename:
                catbox_url = upload_to_catbox(image)
                if catbox_url:
                    asset.image_filename = catbox_url
                    
                    # Update default variation image if no variations were passed
                    default_var = AssetVariation.query.filter_by(asset_id=asset.id).first()
                    if default_var:
                        default_var.image_filename = catbox_url
                    else:
                        new_var = AssetVariation(asset_id=asset.id, name="Default", image_filename=catbox_url)
                        db.session.add(new_var)"""
content = content.replace(search6, replace6)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to routes/seller.py")
