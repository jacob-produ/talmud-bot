from school_manager.models.branch import Branch

q = Branch.query.filter(Branch.symbol.op('regexp')('.*2'))
print(q)
for b in q:
    print(b)
