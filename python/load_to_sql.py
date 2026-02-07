"""
Load HR Recruitment Funnel data into SQLite database
"""

import pandas as pd
import sqlite3
import os

print("=" * 70)
print("LOADING DATA INTO SQL DATABASE")
print("=" * 70)

# Read the recruitment funnel data
print("\n📂 Reading recruitment funnel data...")
df = pd.read_csv('data/hr_recruitment_funnel.csv')
print(f"✅ Loaded {len(df):,} records")

# Create SQLite database
db_path = 'recruitment.db'
print(f"\n💾 Creating SQLite database: {db_path}")
conn = sqlite3.connect(db_path)

# Load data into SQL table
table_name = 'applicant_stages'
df.to_sql(table_name, conn, if_exists='replace', index=False)
print(f"✅ Data loaded into table: {table_name}")

# Verify the data
print(f"\n🔍 Verifying database...")
cursor = conn.cursor()

# Get table info
cursor.execute(f"PRAGMA table_info({table_name})")
columns = cursor.fetchall()
print(f"\nTable Columns ({len(columns)}):")
for col in columns:
    print(f"   {col[1]:.<30} {col[2]}")

# Get row count
cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
count = cursor.fetchone()[0]
print(f"\nTotal Rows: {count:,}")

# Get unique applicants
cursor.execute(f"SELECT COUNT(DISTINCT Applicant_ID) FROM {table_name}")
unique_applicants = cursor.fetchone()[0]
print(f"Unique Applicants: {unique_applicants:,}")

# Get stage distribution
cursor.execute(f"""
    SELECT Stage, COUNT(DISTINCT Applicant_ID) as applicants
    FROM {table_name}
    GROUP BY Stage, Stage_Sequence
    ORDER BY Stage_Sequence
""")
stages = cursor.fetchall()
print(f"\nApplicants by Stage:")
for stage, applicant_count in stages:
    print(f"   {stage:.<35} {applicant_count:>4}")

conn.close()

print("\n" + "=" * 70)
print("✅ DATABASE READY!")
print("=" * 70)
print(f"\nDatabase file: {db_path}")
print(f"Table name: {table_name}")
print(f"\nYou can now run SQL queries using:")
print(f"   sqlite3 {db_path} < sql/funnel_queries.sql")
print("=" * 70)
