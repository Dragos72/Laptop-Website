INSERT INTO Brands(BrandName, CollaborationDate)
VALUES 
    ('Asus', '2024-11-13'),
	('Lenovo', '2024-11-14'),
	('Galaxy', '2024-11-12');


INSERT INTO Laptops (BrandID, CategoryID, ModelName, Price, StockQuantity, Processor, RAM, Storage, GraphicsCard, ScreenSize, Description)
VALUES 
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Asus'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Gaming'), 'Asus Gaming 5', 100.00, 5, 'Intel Core i7', 16, 1024, 'NVIDIA RTX 2060', 15.6, 'Powerful gaming laptop with advanced graphics for immersive gameplay'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Lenovo'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Office'), 'Lenovo ThinkPad T14', 850.00, 20, 'Intel Core i5', 8, 512, 'Integrated Graphics', 14.0, 'Reliable office laptop with great performance for everyday tasks'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Galaxy'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Multi-screen'), 'Galaxy Book Flex', 1200.00, 10, 'Intel Core i7', 16, 512, 'Integrated Graphics', 13.3, 'Sleek laptop with dual screens and touch capabilities for multitasking'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Asus'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Office'), 'Asus VivoBook 15', 600.00, 30, 'Intel Core i3', 8, 256, 'Integrated Graphics', 15.6, 'Affordable office laptop with smooth performance and a large screen'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Lenovo'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Gaming'), 'Lenovo Legion 5', 1500.00, 15, 'AMD Ryzen 7', 16, 1024, 'NVIDIA GTX 1660 Ti', 15.6, 'High-performance gaming laptop with powerful processor and graphics'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Galaxy'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Office'), 'Galaxy NoteBook 9 Pro', 950.00, 25, 'Intel Core i5', 8, 256, 'Integrated Graphics', 15.0, 'Stylish and lightweight office laptop with impressive battery life'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Asus'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Multi-screen'), 'Asus ZenBook Duo', 1800.00, 8, 'Intel Core i7', 16, 512, 'NVIDIA MX250', 14.0, 'Innovative dual-screen laptop designed for productivity and creativity'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Lenovo'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Multi-screen'), 'Lenovo Yoga Book', 1100.00, 10, 'Intel Core i5', 8, 256, 'Integrated Graphics', 13.9, 'Versatile laptop with touch and multi-screen functionality for enhanced workflow'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Galaxy'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Gaming'), 'Galaxy Odyssey', 2000.00, 5, 'Intel Core i9', 32, 2048, 'NVIDIA RTX 2080', 17.3, 'Ultimate gaming laptop with top-of-the-line specs for high-end gaming'),
    ((SELECT BrandID FROM Brands WHERE BrandName = 'Asus'), (SELECT CategoryID FROM Categories WHERE CategoryName = 'Gaming'), 'Asus ROG Strix', 1700.00, 7, 'AMD Ryzen 9', 32, 1024, 'NVIDIA RTX 2070', 15.6, 'High-performance gaming laptop with stunning visuals and fast refresh rate');


SELECT *
FROM Laptops
WHERE ModelName LIKE '%Asus%';








