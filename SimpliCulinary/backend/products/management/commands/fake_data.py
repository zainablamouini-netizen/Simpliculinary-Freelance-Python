import random
from django.core.management.base import BaseCommand
from faker import Faker
from products.models import Category, Product

class Command(BaseCommand):
    help = 'Générer des données fictives pour les catégories et les produits'

    def handle(self, *args, **kwargs):
        fake = Faker(['fr_FR'])
        
        # Création de catégories si elles n'existent pas
        categories_names = ['Électronique', 'Cuisine', 'Maison', 'Sport', 'Beauté']
        categories = []
        for name in categories_names:
            cat, created = Category.objects.get_or_create(name=name)
            categories.append(cat)
            if created:
                self.stdout.write(f"Catégorie '{name}' créée.")

        # Création de produits
        for _ in range(20):
            product = Product.objects.create(
                name=fake.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                price=round(random.uniform(5.0, 1000.0), 2),
                category=random.choice(categories)
            )
            self.stdout.write(f"Produit '{product.name}' créé.")

        self.stdout.write(self.style.SUCCESS(f"Succès : 20 produits fictifs ont été générés !"))
