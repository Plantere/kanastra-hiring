db.getSiblingDB('kanastra_billing').debts.createIndex({ name: 1 });
db.getSiblingDB('kanastra_billing').debts.createIndex({ governmentId: 1 });
db.getSiblingDB('kanastra_billing').debts.createIndex({ debtId: 1 });
db.getSiblingDB('kanastra_billing').debts.createIndex({ email: 1 });
db.getSiblingDB('kanastra_billing').debts.createIndex({ debtAmount: 1 });
db.getSiblingDB('kanastra_billing').debts.createIndex({ debtDueDate: 1 });
db.getSiblingDB('kanastra_billing').debts.createIndex({ debtId: 1 });
db.getSiblingDB('kanastra_billing').debts.createIndex({ taskId: 1 });
