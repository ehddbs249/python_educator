import os
os.environ['SUPABASE_URL'] = 'https://beipxotlrsvibdwddqka.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJlaXB4b3RscnN2aWJkd2RkcWthIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwODQ4NzQsImV4cCI6MjA3OTY2MDg3NH0.uL5QdncXMGwl1XXY0xZ7BCYbnl4hpUD1cD1_HY_ilNA'

from supabase import create_client

try:
    supabase = create_client(
        'https://beipxotlrsvibdwddqka.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJlaXB4b3RscnN2aWJkd2RkcWthIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwODQ4NzQsImV4cCI6MjA3OTY2MDg3NH0.uL5QdncXMGwl1XXY0xZ7BCYbnl4hpUD1cD1_HY_ilNA'
    )
    print("Supabase client created successfully!")

    # 테이블 존재 확인
    response = supabase.rpc('get_pg_tables').execute()
    print(f"Tables: {response.data}")

except Exception as e:
    print(f"Error: {e}")