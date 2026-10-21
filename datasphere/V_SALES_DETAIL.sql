SELECT
    o."ORDER_ID",
    o."LINE_ID",
    o."ORDER_DATE",
    o."MONTH",
    o."PRODUCT_ID",
    o."CUSTOMER_ID",
    o."QUANTITY",
    p."PRODUCT_NAME",
    p."CATEGORY",
    c."SEGMENT",
    c."REGION",
    CAST(
        ROUND(o."QUANTITY" * o."SELLING_PRICE" * (1 - o."DISCOUNT"), 2)
        AS DECIMAL(18,2)
    ) AS "REVENUE",
    CAST(
        ROUND(o."QUANTITY" * k."UNIT_COST", 2)
        AS DECIMAL(18,2)
    ) AS "COGS",
    CAST(
        ROUND(o."QUANTITY" * o."SELLING_PRICE" * (1 - o."DISCOUNT"), 2)
        - ROUND(o."QUANTITY" * k."UNIT_COST", 2)
        AS DECIMAL(18,2)
    ) AS "GROSS_PROFIT"
FROM "ORDERS" o
JOIN "PRODUCT" p
    ON o."PRODUCT_ID" = p."PRODUCT_ID"
JOIN "CUSTOMERS" c
    ON o."CUSTOMER_ID" = c."CUSTOMER_ID"
JOIN "COSTS" k
    ON o."PRODUCT_ID" = k."PRODUCT_ID"
    AND o."MONTH" = k."MONTH"