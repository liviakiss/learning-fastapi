-- SQL Basics — recipes.db
-- Run these one at a time (or as a full script) in DB Browser's Execute SQL tab

-- ============================================
-- Table creation (also doable via DB Browser's Create Table dialog)
-- ============================================
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    servings INTEGER NOT NULL
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,      -- foreign key: points back to recipes.id
    comment TEXT
);

-- ============================================
-- INSERT — adding rows. Text values need single quotes, not backticks.
-- ============================================
INSERT INTO recipes (name, servings) VALUES ('Spotted Dick', 4);
INSERT INTO recipes (name, servings) VALUES ('Tacos', 2);
INSERT INTO recipes (name, servings) VALUES ('Ramen', 6);

-- ============================================
-- SELECT — retrieving data
-- ============================================
SELECT * FROM recipes;

-- WHERE filters which rows are returned
SELECT * FROM recipes WHERE servings > 5;

-- ORDER BY sorts results — ascending by default
SELECT * FROM recipes ORDER BY servings;

-- DESC reverses to descending (largest first)
SELECT * FROM recipes ORDER BY servings DESC;

-- ============================================
-- UPDATE — modifying rows. ALWAYS use WHERE unless you truly mean every row.
-- ============================================
-- Correct: only updates the matching row
UPDATE recipes SET servings = 2 WHERE name = 'Tacos';

-- ============================================
-- DELETE — removing rows. Same WHERE caution as UPDATE.
-- ============================================
-- Removes only a specific row:
-- DELETE FROM recipes WHERE name = 'Tacos';

-- Removes EVERY row (used deliberately here to reset during practice):
-- DELETE FROM recipes;

-- ============================================
-- Foreign keys + JOIN — linking two tables together
-- ============================================
-- Insert reviews pointing at a real recipe id (check your actual ids first —
-- AUTOINCREMENT never reuses numbers, even after DELETE, so these won't
-- necessarily be 1, 2, 3)
INSERT INTO reviews (recipe_id, comment) VALUES (6, 'Delicious!');
INSERT INTO reviews (recipe_id, comment) VALUES (6, 'A bit dry.');

-- JOIN reconstructs the full picture across both tables in one query —
-- reviews never has to store the recipe's name directly
SELECT recipes.name, reviews.comment
FROM reviews
JOIN recipes ON reviews.recipe_id = recipes.id;