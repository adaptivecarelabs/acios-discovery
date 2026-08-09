from acios_discovery.infrastructure.persistence.metadata import Base

print()

print("Registered tables")

print("-" * 60)

for table in Base.metadata.tables:
    print(table)
