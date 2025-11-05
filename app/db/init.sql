DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'companies_db') THEN
      CREATE USER companies_db WITH PASSWORD 'securepassword123';
   END IF;
END
$do$;
