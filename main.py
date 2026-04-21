"""
Домашнє завдання 3. Аналіз даних у PySpark
GoIT Neoversity / Data Engineering

Скрипт виконує шість етапів обробки даних у Apache Spark:
1. Завантаження трьох CSV-файлів у DataFrame.
2. Очищення даних (видалення рядків з пропущеними значеннями).
3. Загальна сума покупок за кожною категорією продуктів.
4. Сума покупок за кожною категорією для вікової категорії 18-25.
5. Частка покупок (%) за кожною категорією від сумарних витрат для 18-25.
6. ТОП-3 категорії з найвищим відсотком витрат для вікової категорії 18-25.
"""

import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def build_spark() -> SparkSession:
    """Створює і повертає SparkSession."""
    return (
        SparkSession.builder
        .appName("goit-de-hw-03")
        .master("local[*]")
        .getOrCreate()
    )


def main() -> None:
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    data_dir = os.path.dirname(os.path.abspath(__file__))
    users_path = os.path.join(data_dir, "users.csv")
    purchases_path = os.path.join(data_dir, "purchases.csv")
    products_path = os.path.join(data_dir, "products.csv")

    # ------------------------------------------------------------------
    # Етап 1. Завантаження CSV-файлів у DataFrame
    # ------------------------------------------------------------------
    users_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(users_path)
    )

    purchases_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(purchases_path)
    )

    products_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(products_path)
    )

    print("\n=== Етап 1. Вхідні DataFrame-и ===")
    print("users_df:")
    users_df.show(truncate=False)
    print("purchases_df:")
    purchases_df.show(truncate=False)
    print("products_df:")
    products_df.show(truncate=False)

    # ------------------------------------------------------------------
    # Етап 2. Очищення даних (видалити рядки з пропущеними значеннями)
    # ------------------------------------------------------------------
    users_clean = users_df.dropna()
    purchases_clean = purchases_df.dropna()
    products_clean = products_df.dropna()

    print("\n=== Етап 2. Очищені DataFrame-и ===")
    print(
        f"users: було {users_df.count()} -> стало {users_clean.count()}"
    )
    print(
        f"purchases: було {purchases_df.count()} -> стало {purchases_clean.count()}"
    )
    print(
        f"products: було {products_df.count()} -> стало {products_clean.count()}"
    )
    users_clean.show(truncate=False)
    purchases_clean.show(truncate=False)
    products_clean.show(truncate=False)

    # ------------------------------------------------------------------
    # Етап 3. Загальна сума покупок за кожною категорією продуктів
    # ------------------------------------------------------------------
    # Сума покупки = price * quantity
    purchases_with_products = purchases_clean.join(
        products_clean, on="product_id", how="inner"
    ).withColumn(
        "total_amount", F.col("price") * F.col("quantity")
    )

    category_totals = (
        purchases_with_products
        .groupBy("category")
        .agg(F.round(F.sum("total_amount"), 2).alias("total_sales"))
        .orderBy(F.desc("total_sales"))
    )

    print("\n=== Етап 3. Загальна сума покупок за категоріями ===")
    category_totals.show(truncate=False)

    # ------------------------------------------------------------------
    # Етап 4. Сума покупок за категоріями для вікової категорії 18-25
    # ------------------------------------------------------------------
    users_18_25 = users_clean.filter(
        (F.col("age") >= 18) & (F.col("age") <= 25)
    )

    purchases_18_25 = (
        purchases_clean
        .join(users_18_25, on="user_id", how="inner")
        .join(products_clean, on="product_id", how="inner")
        .withColumn("total_amount", F.col("price") * F.col("quantity"))
    )

    category_totals_18_25 = (
        purchases_18_25
        .groupBy("category")
        .agg(F.round(F.sum("total_amount"), 2).alias("total_sales"))
        .orderBy(F.desc("total_sales"))
    )

    print("\n=== Етап 4. Сума покупок за категоріями (вік 18-25) ===")
    category_totals_18_25.show(truncate=False)

    # ------------------------------------------------------------------
    # Етап 5. Частка покупок (%) за кожною категорією від сумарних витрат
    #         для вікової категорії 18-25
    # ------------------------------------------------------------------
    grand_total_18_25 = (
        purchases_18_25
        .agg(F.sum("total_amount").alias("grand_total"))
        .collect()[0]["grand_total"]
    )

    category_share_18_25 = (
        category_totals_18_25
        .withColumn(
            "percentage",
            F.round(F.col("total_sales") / F.lit(grand_total_18_25) * 100, 2),
        )
        .orderBy(F.desc("percentage"))
    )

    print("\n=== Етап 5. Частка покупок (%) за категоріями (вік 18-25) ===")
    category_share_18_25.show(truncate=False)

    # ------------------------------------------------------------------
    # Етап 6. ТОП-3 категорії з найвищим відсотком витрат для 18-25
    # ------------------------------------------------------------------
    top_3_categories = category_share_18_25.limit(3)

    print("\n=== Етап 6. ТОП-3 категорії за відсотком витрат (вік 18-25) ===")
    top_3_categories.show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
