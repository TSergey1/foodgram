ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@admin.com
ADMIN_PASSWORD=1111

# Выполнить миграции
python manage.py migrate

# Создать суперпользователя
echo "from django.contrib.auth import get_user_model; User = get_user_model();
User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | python manage.py shell

# Создать теги
add_tag() {
    name="$1"
    color="$2"
    slug="$3"

    # <recipes.models> - заменить на выш путь к файлу моделей.
    # <Tag> - заменить на имя вашего класса тегов.
    echo "from recipes.models import Tag;
Tag.objects.create(name='$name', color='$color', slug='$slug')" | python manage.py shell
}
add_tag "Завтрак" "#FF0000" "breakfast"
add_tag "Обед" "#00FF00" "lunch"
add_tag "Ужин" "#0000FF" "dinner"

# Создать ингредиент
add_ingredient() {
    name="$1"
    measurement_unit="$2"

    # <recipes.models> - заменить на выш путь к файлу моделей.
    # <Ingredient> - заменить на имя вашего класса ингредиентов.
    echo "from recipes.models import Ingredient;
Ingredient.objects.create(name='$name', measurement_unit='$measurement_unit')" | python manage.py shell
}
add_ingredient "Капуста" "кг"
add_ingredient "Молоко" "л"

# Запустить сервер
python manage.py runserver