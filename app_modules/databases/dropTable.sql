set transaction read write; 
BEGIN TRANSACTION;
DROP TABLE IF EXISTS "password_manager";
DROP TABLE IF EXISTS "role_manager";
DROP TABLE IF EXISTS "user_question_answer";
DROP TABLE IF EXISTS "security_question";
DROP TABLE IF EXISTS "income";
DROP TABLE IF EXISTS "expense";
DROP TABLE IF EXISTS "transaction_comment";
DROP TABLE IF EXISTS "transaction_log";
DROP TABLE IF EXISTS "payment_method";
DROP TABLE IF EXISTS "collection";
DROP TABLE IF EXISTS "collection_type";
DROP TABLE IF EXISTS "account";
DROP TABLE IF EXISTS "account_type";
DROP TABLE IF EXISTS "flat_owner";
DROP TABLE IF EXISTS "member";
DROP TABLE IF EXISTS "flat";
DROP TABLE IF EXISTS "user";
DROP TABLE IF EXISTS "user_role";
DROP TABLE IF EXISTS "society";
DROP TABLE IF EXISTS "country_currency";
COMMIT;