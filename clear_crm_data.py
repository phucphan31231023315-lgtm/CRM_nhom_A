# Clear transaction data for Sgroup CRM
print("Starting database clean up...")

# 1. Delete assignment history
history_count = env['sgroup.assignment.history'].search([]).unlink()
print(f"Cleared {history_count} Assignment History records.")

# 2. Delete revenues
revenue_count = env['sgroup.revenue'].search([]).unlink()
print(f"Cleared {revenue_count} Revenue records.")

# 3. Delete customers
customer_count = env['sgroup.customer'].search([]).unlink()
print(f"Cleared {customer_count} Customer records.")

# 4. Delete ad data (leads)
lead_count = env['sgroup.ad.data'].search([]).unlink()
print(f"Cleared {lead_count} Ad Data / Lead records.")

# 5. Reset round-robin counts in rules
rule_lines = env['sgroup.assignment.rule.line'].search([])
if rule_lines:
    rule_lines.write({'assigned_count': 0})
print("Reset assigned counts for all Assignment Rules.")

env.cr.commit()
print("Database cleanup completed successfully!")
