import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import User
from catalog.models import Category, SubCategory, Brand, Size, Color, Product, ProductVariant
from customers.models import Customer
from suppliers.models import Supplier
from purchases.models import Purchase, PurchaseItem
from sales.models import Sale, SaleItem
from payments.models import Payment
from expenses.models import Expense
from returns_exchanges.models import Return, ReturnItem
from offers.models import Offer
from shopsettings.models import ShopSettings
from inventory.models import record_stock_movement

FIRST_NAMES = ["Ravi", "Suresh", "Lakshmi", "Priya", "Anil", "Kavya", "Venkatesh", "Sneha", "Ramesh", "Divya",
               "Krishna", "Anitha", "Sai", "Pooja", "Naveen", "Swathi", "Prasad", "Meena", "Vijay", "Rekha"]
LAST_NAMES = ["Reddy", "Rao", "Naidu", "Kumar", "Sharma", "Varma", "Chowdary", "Prasad", "Devi", "Babu"]

CATEGORY_DATA = {
    "MEN": ["Shirts", "T-Shirts", "Jeans", "Trousers", "Formal Wear", "Casual Wear", "Ethnic Wear", "Jackets", "Inner Wear", "Accessories"],
    "WOMEN": ["Sarees", "Chudidars", "Kurtis", "Tops", "Dresses", "Jeans", "Leggings", "Salwar Suits", "Ethnic Wear", "Western Wear", "Night Wear", "Accessories"],
    "BOYS": ["Shirts", "T-Shirts", "Jeans", "Shorts", "Trousers", "Ethnic Wear", "Party Wear", "School Wear"],
    "GIRLS": ["Dresses", "Frocks", "Tops", "Skirts", "Jeans", "Leggings", "Ethnic Wear", "Party Wear", "Traditional Wear"],
    "KIDS": ["Baby Boys", "Baby Girls", "Newborn", "Kids Sets", "Night Wear", "Party Wear", "Seasonal Wear"],
}
CATEGORY_ICONS = {"MEN": "👔", "WOMEN": "👗", "BOYS": "🧒", "GIRLS": "👧", "KIDS": "🧸"}

BRANDS = ["Raymond", "Peter England", "Fabindia", "Biba", "W for Woman", "Allen Solly", "Van Heusen",
          "Global Desi", "Pantaloons", "Levi's", "United Colors of Benetton", "House of Pataudi"]

ADULT_SIZES = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
KID_SIZES = ["0-3 Months", "3-6 Months", "6-12 Months", "1-2 Years", "2-3 Years", "3-4 Years", "4-5 Years",
             "5-6 Years", "6-7 Years", "7-8 Years", "8-10 Years", "10-12 Years", "12-14 Years"]
COLORS = [("Red", "#DC2626"), ("Blue", "#2563EB"), ("Black", "#111827"), ("White", "#F9FAFB"),
          ("Green", "#16A34A"), ("Yellow", "#EAB308"), ("Pink", "#EC4899"), ("Maroon", "#7F1D1D"),
          ("Navy", "#1E3A8A"), ("Beige", "#D6C9A8"), ("Grey", "#6B7280"), ("Orange", "#EA580C")]

PRODUCT_NAME_TEMPLATES = {
    "Shirts": ["Slim Fit Cotton Shirt", "Formal Checked Shirt", "Linen Casual Shirt", "Printed Party Shirt"],
    "T-Shirts": ["Round Neck T-Shirt", "Polo T-Shirt", "Graphic Print Tee", "Full Sleeve T-Shirt"],
    "Jeans": ["Slim Fit Jeans", "Straight Fit Jeans", "Distressed Jeans", "Skinny Jeans"],
    "Trousers": ["Formal Trousers", "Chino Trousers", "Cargo Trousers"],
    "Formal Wear": ["3-Piece Formal Suit", "Formal Blazer Set"],
    "Casual Wear": ["Casual Co-ord Set", "Weekend Casual Shirt"],
    "Ethnic Wear": ["Silk Kurta Set", "Cotton Kurta Pajama", "Nehru Jacket Set"],
    "Jackets": ["Denim Jacket", "Bomber Jacket", "Wind Cheater"],
    "Inner Wear": ["Cotton Vest Pack", "Boxer Shorts Pack"],
    "Accessories": ["Leather Belt", "Cotton Handkerchief Set", "Formal Necktie"],
    "Sarees": ["Kanjeevaram Silk Saree", "Banarasi Silk Saree", "Cotton Handloom Saree", "Georgette Party Saree"],
    "Chudidars": ["Printed Chudidar Set", "Embroidered Chudidar Set"],
    "Kurtis": ["Anarkali Kurti", "Straight Cut Kurti", "A-Line Kurti"],
    "Tops": ["Floral Print Top", "Solid Crop Top", "Off-Shoulder Top"],
    "Dresses": ["Floral Maxi Dress", "A-Line Party Dress", "Denim Shirt Dress"],
    "Leggings": ["Ankle Length Leggings", "Churidar Leggings"],
    "Salwar Suits": ["Cotton Salwar Suit", "Georgette Salwar Suit"],
    "Western Wear": ["Denim Jumpsuit", "Palazzo Set"],
    "Night Wear": ["Cotton Night Suit", "Satin Nightgown"],
    "Frocks": ["Party Frock", "Cotton Printed Frock"],
    "Skirts": ["Pleated Skirt", "Denim Skirt"],
    "Traditional Wear": ["Pattu Langa Voni", "Half Saree Set"],
    "Shorts": ["Denim Shorts", "Cotton Cargo Shorts"],
    "School Wear": ["School Uniform Shirt", "School Uniform Trouser"],
    "Party Wear": ["Sequin Party Dress", "Bow-Tie Party Shirt"],
    "Baby Boys": ["Baby Boy Romper", "Baby Boy Dungaree Set"],
    "Baby Girls": ["Baby Girl Frock", "Baby Girl Romper"],
    "Newborn": ["Newborn Gift Set", "Newborn Cotton Onesie"],
    "Kids Sets": ["Kids Co-ord Set", "Kids Ethnic Set"],
    "Seasonal Wear": ["Kids Winter Jacket", "Kids Raincoat"],
}


class Command(BaseCommand):
    help = "Seeds realistic demo data for the SRI KRISHNA clothing store system."

    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write("Seeding SRI KRISHNA demo data...")

        shop = ShopSettings.get_solo()
        shop.google_maps_embed_url = "https://www.google.com/maps?q=Narasapur,Andhra+Pradesh&output=embed"
        shop.facebook_url = "https://facebook.com/srikrishnaclothing"
        shop.instagram_url = "https://instagram.com/srikrishnaclothing"
        shop.save()

        self.create_users()
        categories = self.create_categories()
        brands = self.create_brands()
        sizes = self.create_sizes()
        colors = self.create_colors()
        products = self.create_products(categories, brands, sizes, colors)
        suppliers = self.create_suppliers()
        for p in products:
            if not p.supplier_id:
                p.supplier = random.choice(suppliers)
                p.save(update_fields=["supplier"])
        customers = self.create_customers()
        self.create_purchases(suppliers, products)
        sales = self.create_sales(customers, products)
        self.create_expenses()
        self.create_returns(sales)
        self.create_offers(categories)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("Login: admin / admin123 (Super Admin)"))
        self.stdout.write(self.style.SUCCESS("Also try: manager1/manager123, cashier1/cashier123"))

    def create_users(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@srikrishna.in", "admin123",
                                           first_name="Krishna", last_name="Owner", role=User.Role.SUPER_ADMIN,
                                           phone="9876543210", date_joined_shop=date(2018, 1, 1))
        if not User.objects.filter(username="manager1").exists():
            User.objects.create_user("manager1", "manager1@srikrishna.in", "manager123",
                                      first_name="Suresh", last_name="Manager", role=User.Role.MANAGER,
                                      phone="9876500001", date_joined_shop=date(2020, 6, 1), is_staff=True)
        if not User.objects.filter(username="cashier1").exists():
            User.objects.create_user("cashier1", "cashier1@srikrishna.in", "cashier123",
                                      first_name="Priya", last_name="Cashier", role=User.Role.CASHIER,
                                      phone="9876500002", date_joined_shop=date(2022, 3, 15), is_staff=True)
        if not User.objects.filter(username="staff1").exists():
            User.objects.create_user("staff1", "staff1@srikrishna.in", "staff123",
                                      first_name="Naveen", last_name="Staff", role=User.Role.STAFF,
                                      phone="9876500003", date_joined_shop=date(2023, 1, 10), is_staff=True)

    def create_categories(self):
        cats = {}
        for order, (name, subs) in enumerate(CATEGORY_DATA.items()):
            cat, _ = Category.objects.get_or_create(
                name=name.title(), defaults={"slug": name.lower(), "icon": CATEGORY_ICONS[name], "display_order": order}
            )
            cat.slug = name.lower()
            cat.save()
            cats[name] = {"obj": cat, "subs": {}}
            for sub_name in subs:
                sub, _ = SubCategory.objects.get_or_create(category=cat, name=sub_name, defaults={"slug": slugify(sub_name)})
                cats[name]["subs"][sub_name] = sub
        return cats

    def create_brands(self):
        return [Brand.objects.get_or_create(name=b)[0] for b in BRANDS]

    def create_sizes(self):
        sizes = {}
        for i, s in enumerate(ADULT_SIZES):
            sizes[s] = Size.objects.get_or_create(label=s, defaults={"display_order": i})[0]
        for i, s in enumerate(KID_SIZES):
            sizes[s] = Size.objects.get_or_create(label=s, defaults={"display_order": 100 + i})[0]
        return sizes

    def create_colors(self):
        return {name: Color.objects.get_or_create(name=name, defaults={"hex_code": hexcode})[0] for name, hexcode in COLORS}

    def create_suppliers(self):
        suppliers = []
        supplier_names = ["Andhra Textiles Pvt Ltd", "Krishna Fabrics", "Godavari Garments", "Sri Lakshmi Weavers",
                           "Vijayawada Cloth Traders", "Hyderabad Fashion Hub", "Coastal Cotton Mills",
                           "Rajahmundry Silk House", "Amaravati Apparels", "Deccan Textile Suppliers"]
        for i, name in enumerate(supplier_names):
            s, _ = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    "company_name": name, "mobile": f"90000{i:05d}"[-10:], "email": f"contact{i}@supplier.in",
                    "address": f"Industrial Area, Phase {i+1}, Andhra Pradesh",
                    "gst_number": f"37AAACS{1000+i}F1Z{i%9}",
                },
            )
            suppliers.append(s)
        return suppliers

    def create_products(self, categories, brands, sizes, colors):
        products = []
        sku_counter = 1000
        for cat_key, cat_info in categories.items():
            cat_obj = cat_info["obj"]
            for sub_name, sub_obj in cat_info["subs"].items():
                templates = PRODUCT_NAME_TEMPLATES.get(sub_name, [f"{sub_name} Item"])
                for template in templates[:2]:
                    if len(products) >= 60:
                        break
                    sku_counter += 1
                    sku = f"SK{sku_counter}"
                    name = f"{template}"
                    slug = slugify(f"{name}-{sku}")
                    purchase_price = Decimal(random.randint(250, 1800))
                    selling_price = (purchase_price * Decimal(random.uniform(1.4, 2.2))).quantize(Decimal("1"))
                    mrp = (selling_price * Decimal(random.uniform(1.05, 1.3))).quantize(Decimal("1"))
                    discount = Decimal(random.choice([0, 0, 10, 15, 20, 25]))
                    gst = Decimal(random.choice([5, 12, 18]))
                    gender_map = {"MEN": "MEN", "WOMEN": "WOMEN", "BOYS": "BOYS", "GIRLS": "GIRLS", "KIDS": "KIDS"}

                    product = Product.objects.create(
                        sku=sku, name=name, slug=slug, category=cat_obj, subcategory=sub_obj,
                        gender=gender_map[cat_key], brand=random.choice(brands),
                        fabric=random.choice(["Cotton", "Silk", "Linen", "Polyester", "Denim", "Georgette"]),
                        description=f"{name} from SRI KRISHNA's {cat_obj.name} collection. Comfortable fit and premium fabric.",
                        purchase_price=purchase_price, selling_price=selling_price, mrp=mrp,
                        discount_percent=discount, gst_percent=gst, minimum_stock=5,
                        is_active=True, is_new_arrival=random.random() < 0.25, is_best_seller=random.random() < 0.2,
                    )
                    size_pool = list(sizes.values()) if cat_key in ("KIDS",) else \
                        [sizes[s] for s in ADULT_SIZES] if cat_key in ("MEN", "WOMEN") else \
                        [sizes[s] for s in ADULT_SIZES[:5]]
                    chosen_sizes = random.sample(size_pool, k=min(3, len(size_pool)))
                    chosen_colors = random.sample(list(colors.values()), k=2)
                    for sz in chosen_sizes:
                        for col in chosen_colors:
                            ProductVariant.objects.create(
                                product=product, size=sz, color=col, stock_quantity=random.randint(0, 40)
                            )
                    products.append(product)
        return products

    def create_customers(self):
        customers = []
        for i in range(20):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            mobile = f"9{random.randint(100000000, 999999999)}"
            c, created = Customer.objects.get_or_create(
                mobile=mobile, defaults={
                    "name": name, "email": f"{name.split()[0].lower()}{i}@example.com",
                    "address": "Narasapur, Andhra Pradesh", "loyalty_points": random.randint(0, 300),
                },
            )
            customers.append(c)
        return customers

    def create_purchases(self, suppliers, products):
        admin = User.objects.get(username="admin")
        for i in range(15):
            supplier = random.choice(suppliers)
            pdate = timezone.localdate() - timedelta(days=random.randint(5, 120))
            purchase = Purchase.objects.create(
                purchase_invoice_number=f"PUR-{100000+i}", supplier=supplier, date=pdate,
                payment_status=random.choice(["PAID", "PENDING", "PARTIALLY_PAID"]),
                amount_paid=Decimal(0), created_by=admin,
            )
            chosen_products = random.sample(products, k=min(4, len(products)))
            for prod in chosen_products:
                variant = prod.variants.first()
                if not variant:
                    continue
                qty = random.randint(5, 20)
                PurchaseItem.objects.create(
                    purchase=purchase, variant=variant, quantity=qty,
                    purchase_price=prod.purchase_price, gst_percent=prod.gst_percent,
                )
                record_stock_movement(variant, stock_added=qty, reason="PURCHASE", reference=purchase.purchase_invoice_number, employee=admin)
            purchase.recalc_total()
            purchase.amount_paid = purchase.grand_total if purchase.payment_status == "PAID" else \
                (purchase.grand_total / 2 if purchase.payment_status == "PARTIALLY_PAID" else Decimal(0))
            purchase.save()

    def create_sales(self, customers, products):
        cashiers = list(User.objects.filter(role__in=[User.Role.CASHIER, User.Role.MANAGER, User.Role.SUPER_ADMIN]))
        sales = []
        for i in range(40):
            sdate = timezone.now() - timedelta(days=random.randint(0, 60), hours=random.randint(0, 10))
            customer = random.choice(customers) if random.random() < 0.7 else None
            cashier = random.choice(cashiers)
            sale = Sale.objects.create(
                invoice_number=f"SK-{200000+i}", customer=customer, cashier=cashier, status="COMPLETED",
            )
            sale.created_at = sdate
            subtotal = Decimal("0")
            gst_total = Decimal("0")
            discount_total = Decimal("0")
            chosen_products = random.sample(products, k=min(random.randint(1, 4), len(products)))
            for prod in chosen_products:
                variant = random.choice(list(prod.variants.all())) if prod.variants.exists() else None
                if not variant or variant.stock_quantity < 1:
                    continue
                qty = min(random.randint(1, 2), variant.stock_quantity)
                price = prod.effective_price
                item_discount = Decimal("0")
                gst_percent = prod.gst_percent
                item = SaleItem.objects.create(
                    sale=sale, variant=variant, quantity=qty, unit_price=price,
                    discount_amount=item_discount, gst_percent=gst_percent,
                )
                subtotal += price * qty
                gst_total += (price * qty) * (gst_percent / Decimal(100))
                record_stock_movement(variant, stock_sold=qty, reason="SALE", reference=sale.invoice_number, employee=cashier)
            if not sale.items.exists():
                sale.delete()
                continue
            grand_total = subtotal - discount_total + gst_total
            sale.subtotal = round(subtotal, 2)
            sale.discount_amount = round(discount_total, 2)
            sale.gst_amount = round(gst_total, 2)
            sale.grand_total = round(grand_total, 2)
            points = int((grand_total // 100) * 2)
            sale.loyalty_points_earned = points
            sale.save()
            Payment.objects.create(
                transaction_id=f"TXN{100000+i}", sale=sale, customer=customer, amount=sale.grand_total,
                method=random.choice(["CASH", "UPI", "CARD", "CASH", "UPI"]), status="PAID",
            )
            sales.append(sale)
        return sales

    def create_expenses(self):
        admin = User.objects.get(username="admin")
        categories = ["RENT", "ELECTRICITY", "SALARY", "TRANSPORT", "INTERNET", "MAINTENANCE", "MARKETING", "PACKAGING", "MISC"]
        for i in range(25):
            edate = timezone.localdate() - timedelta(days=random.randint(0, 90))
            Expense.objects.create(
                date=edate, category=random.choice(categories),
                description=f"Monthly expense entry #{i+1}",
                amount=Decimal(random.randint(500, 15000)),
                payment_method=random.choice(["CASH", "UPI", "BANK_TRANSFER"]),
                employee=admin,
            )

    def create_returns(self, sales):
        admin = User.objects.get(username="admin")
        eligible = [s for s in sales if s.items.exists()]
        for sale in random.sample(eligible, k=min(5, len(eligible))):
            item = sale.items.first()
            ret = Return.objects.create(
                return_number=f"RET-{300000 + sale.id}", sale=sale, return_type="RETURN", resolution="REFUND",
                reason="Size did not fit properly.", processed_by=admin, refund_amount=item.unit_price,
            )
            ReturnItem.objects.create(ret=ret, original_sale_item=item, quantity=1)
            record_stock_movement(item.variant, stock_added=1, reason="RETURN", reference=ret.return_number, employee=admin)

    def create_offers(self, categories):
        today = timezone.localdate()
        Offer.objects.get_or_create(
            title="Festival Sale - Up to 50% OFF",
            defaults={
                "offer_type": "FESTIVAL", "description": "Celebrate the festive season with massive discounts across all categories.",
                "discount_value": Decimal(50), "minimum_purchase": Decimal(999), "maximum_discount": Decimal(1500),
                "start_date": today - timedelta(days=5), "end_date": today + timedelta(days=25), "is_active": True,
            },
        )
        offer2, _ = Offer.objects.get_or_create(
            title="Flat 20% Off on Ethnic Wear",
            defaults={
                "offer_type": "PERCENTAGE", "description": "Get flat 20% off on all ethnic wear this month.",
                "discount_value": Decimal(20), "minimum_purchase": Decimal(500),
                "start_date": today - timedelta(days=2), "end_date": today + timedelta(days=15), "is_active": True,
            },
        )
        Offer.objects.get_or_create(
            title="Kids Wear Buy 1 Get 1",
            defaults={
                "offer_type": "BOGO", "description": "Buy any kids wear item and get one free on select styles.",
                "discount_value": Decimal(100), "minimum_purchase": Decimal(0),
                "start_date": today - timedelta(days=1), "end_date": today + timedelta(days=10), "is_active": True,
            },
        )
