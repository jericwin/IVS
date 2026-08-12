from app import app
from models import db, Asset, Transaction

with app.app_context():
    asset = Asset.query.order_by(Asset.id.desc()).first()
    if asset:
        print(f"Asset ID: {asset.id}")
        print(f"Image filename: {asset.image_filename}")
        print("Variations:")
        for v in asset.variations:
            print(f" - {v.name}: {v.image_filename}")
    else:
        print("No assets found")
