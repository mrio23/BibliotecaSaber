SELECT enumlabel
FROM pg_enum
WHERE enumtypid = 'status_emprestimo'::regtype;