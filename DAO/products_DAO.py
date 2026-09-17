# @Author: Sheep Wang
# @File: products_DAO.py
# @Created: 2026-09-03 22:15
# @Description: products_DAO.py



from utils.DB_utils import get_db_connection
from model.products_model import (
    ProductCreate,
    ProductQuery,
    ProductsRequestUpdate
)





class ProductsDAO:

    # Select products sql
    @staticmethod
    def select_product(query: ProductQuery) -> list:
        """
        Query products based on dynamic filters (supports partial filters or full scan if all are None).
        """
        sql = "SELECT * FROM products WHERE 1=1"
        params = []

        # 1. Check if name filter is provided
        if query.name is not None and query.name.strip() != "":
            sql += " AND name LIKE %s"
            params.append(f"%{query.name.strip()}%")

        # 2. Check if ids filter is provided
        if query.ids is not None and len(query.ids) > 0:
            # Using FIND_IN_SET or IN clause for list of IDs
            format_strings = ','.join(['%s'] * len(query.ids))
            sql += f" AND id IN ({format_strings})"
            params.extend(query.ids)

        # 3. Check price filter if needed
        if query.price is not None:
            sql += " AND price = %s"
            params.append(query.price)

        # Execute query (make sure it's cursor.execute)
        connection = get_db_connection()  # get DB connection
        cursor = connection.cursor()      # Creat cursor
        try:
            cursor.execute(sql, tuple(params))
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
            connection.close()


    # Create new data
    @staticmethod
    def insert_product(data: ProductCreate) -> int:
        sql = "INSERT INTO products (name, price, stock, description) VALUES (%s, %s, %s, %s)"
        params = (data.name, data.price, data.stock, data.description)

        # Connect DB
        conn = get_db_connection()

        #Run sql to insert data
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                conn.commit()                                  # Submit data
                return cursor.lastrowid                        # Return inserted data

        finally:
            conn.close()



    # Modify data
    @staticmethod
    def update_produt(data: ProductsRequestUpdate) -> int:
        # Just modify fields with values passed by front-end
        set_clauses = []
        params = []

        # The values with passed from front-end include "name"  
        if data.name is not None:
            set_clauses.append("name = %s")
            params.append(data.name)


        # The values with passed from front-end include "price"  
        if data.price is not None:
            set_clauses.append("price = %s")
            params.append(data.price)

        # The values with passed from front-end include "stock"  
        if data.stock is not None:
            set_clauses.append("stock = %s")
            params.append(data.stock)

        # The values with passed from front-end include "description"  
        if data.description is not None:
            set_clauses.append("description = %s")
            params.append(data.description)

        # If no field be modified 
        if not set_clauses:
            return 0

        # Base sql of insert
        sql = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = %s"
        params.append(data.id)                                                     # Put the id of Where clause at the end of the paramater list

        # Conenect DB
        conn = get_db_connection()

        # Run sql to modify data
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                conn.commit()
                return cursor.rowcount                 # Return rows impacted

        finally:
            conn.close()



    # Batch Delete
    @staticmethod
    def delete_products_by_ids(ids: list[int]) -> int:
        # Not data to delete     
        if not ids:
            return 0

        # Generate del sql
        placeholders = ", ".join(["%s"]*len(ids))
        sql = f"DELETE FROM products WHERE id IN ({placeholders})"

        # Connect DB
        conn = get_db_connection()

        # Run sql to del data
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(ids))
                conn.commit()
                return cursor.rowcount                # Return rows impacted

        finally:
            conn.close()