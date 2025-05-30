import os
import shutil

# u0421u043fu0438u0441u043eu043a u0444u0430u0439u043bu043eu0432, u043au043eu0442u043eu0440u044bu0435 u043du0443u0436u043du043e u0443u0434u0430u043bu0438u0442u044c
files_to_remove = [
    'clean_test_messages.py',
    'create_test_users.py',
    'freelance_core/create_test_data.py',
    'purge_all_test_data.py',
    'migrate_to_postgres.py',
    'setup_postgres.py',
    'setup_postgres_db.py',
    'db_export.py',
    'create_database.py',
    'create_db.sql',
    'setup_db.sql',
    'check_deployment.py',
    'clean_demo_conversation.py',
    'fix_line.txt',
    'fix_ssl_config.py',
    'generate_ssl_cert.py',
    'run_dev_server.bat',
    'run_ssl_server.bat',
    'cleanup_list.txt',
    'fix_line.txt',
]

# u0421u043fu0438u0441u043eu043a u0444u0430u0439u043bu043eu0432 u0444u0438u043au0441u0442u0443u0440, u043au043eu0442u043eu0440u044bu0435 u043du0443u0436u043du043e u0443u0434u0430u043bu0438u0442u044c 
# (u043eu0441u0442u0430u0432u043bu044fu0435u043c u0442u043eu043bu044cu043au043e business_categories_simple.json)
fixture_files = [
    'jobs/fixtures/initial_categories.json',
    'jobs/fixtures/categories.json',
    'jobs/fixtures/initial_tags.json',
    'jobs/fixtures/tags.json',
    'jobs/fixtures/business_categories.json',
]

def cleanup_project():
    print("u041du0430u0447u0430u043bu043e u043eu0447u0438u0441u0442u043au0438 u043fu0440u043eu0435u043au0442u0430...")
    
    # u0423u0434u0430u043bu0435u043du0438u0435 u0444u0430u0439u043bu043eu0432
    for file_path in files_to_remove:
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"u0423u0434u0430u043bu0435u043d u0444u0430u0439u043b: {file_path}")
            except Exception as e:
                print(f"u041eu0448u0438u0431u043au0430 u043fu0440u0438 u0443u0434u0430u043bu0435u043du0438u0438 {file_path}: {e}")
    
    # u0423u0434u0430u043bu0435u043du0438u0435 u0444u0430u0439u043bu043eu0432 u0444u0438u043au0441u0442u0443u0440
    for fixture_path in fixture_files:
        full_path = os.path.join(os.getcwd(), fixture_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"u0423u0434u0430u043bu0435u043d u0444u0430u0439u043b u0444u0438u043au0441u0442u0443u0440u044b: {fixture_path}")
            except Exception as e:
                print(f"u041eu0448u0438u0431u043au0430 u043fu0440u0438 u0443u0434u0430u043bu0435u043du0438u0438 {fixture_path}: {e}")
    
    # u041fu0435u0440u0435u0438u043cu0435u043du043eu0432u0430u043du0438u0435 u0444u0430u0439u043bu0430 u0444u0438u043au0441u0442u0443u0440u044b u0431u0438u0437u043du0435u0441-u043au0430u0442u0435u0433u043eu0440u0438u0439
    business_categories_path = os.path.join(os.getcwd(), 'jobs/fixtures/business_categories_simple.json')
    if os.path.exists(business_categories_path):
        new_path = os.path.join(os.getcwd(), 'jobs/fixtures/categories.json')
        try:
            shutil.copy2(business_categories_path, new_path)
            os.remove(business_categories_path)
            print("u0424u0430u0439u043b business_categories_simple.json u043fu0435u0440u0435u0438u043cu0435u043du043eu0432u0430u043d u0432 categories.json")
        except Exception as e:
            print(f"u041eu0448u0438u0431u043au0430 u043fu0440u0438 u043fu0435u0440u0435u0438u043cu0435u043du043eu0432u0430u043du0438u0438 u0444u0430u0439u043bu0430 u0444u0438u043au0441u0442u0443u0440u044b: {e}")
    
    print("u041eu0447u0438u0441u0442u043au0430 u043fu0440u043eu0435u043au0442u0430 u0437u0430u0432u0435u0440u0448u0435u043du0430!")

if __name__ == "__main__":
    cleanup_project()
