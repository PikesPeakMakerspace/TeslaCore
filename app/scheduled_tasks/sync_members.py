import os
import json
import requests
import logging
import pymysql
from app.database import db
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger('sync_members')


def sync_members():
    """
    Syncs new members from make.com to a remote MariaDB database
    """
    from app.app import app
    with app.app_context():
        try:
            # 1. Make request to make.com endpoint
            add_member_uri = os.environ.get('ADD_MEMBER_URI')
            add_member_key = os.environ.get('ADD_MEMBER_KEY')
            
            if not add_member_uri or not add_member_key:
                logger.error("Missing required environment variables: ADD_MEMBER_URI or ADD_MEMBER_KEY")
                return
                
            url = f"https://hook.us2.make.com/{add_member_uri}?key={add_member_key}"
            
            logger.info("Requesting member data from make.com")
            response = requests.get(url)
            if response.status_code != 200:
                logger.error(f"Failed to fetch members from make.com: {response.status_code}")
                return
            
            # 2. Parse the JSON response
            try:
                members = json.loads(response.text)
                if not members:
                    logger.info("No new members to sync")
                    return
                
                logger.info(f"Retrieved {len(members)} members from make.com")
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON response")
                return

            # 3. Connect to MariaDB and insert/update members
            try:
                # Get database connection parameters from environment
                db_host = os.environ.get('REMOTE_DB_HOST')
                db_port = int(os.environ.get('REMOTE_DB_PORT', 3306))
                db_user = os.environ.get('REMOTE_DB_USER')
                db_password = os.environ.get('REMOTE_DB_PASSWORD')
                db_name = os.environ.get('REMOTE_DB_NAME')
                
                if not all([db_host, db_user, db_password, db_name]):
                    logger.error("Missing required database configuration variables")
                    return
                
                # Connect to the database
                logger.info(f"Connecting to remote database at {db_host}")
                connection = pymysql.connect(
                    host=db_host,
                    port=db_port,
                    user=db_user,
                    password=db_password,
                    database=db_name,
                    cursorclass=pymysql.cursors.DictCursor
                )
                
                new_members_count = 0
                with connection.cursor() as cursor:
                    # Insert each member if they don't already exist
                    for member in members:
                        card = str(member.get('card', ''))
                        name = member.get('name', '')
                        
                        if not card or not name:
                            logger.warning(f"Skipping member with missing data: {member}")
                            continue
                        
                        # Check if member already exists with this badge_id
                        cursor.execute("SELECT id FROM user WHERE badge_id = %s", (card,))
                        existing_member = cursor.fetchone()
                        
                        if not existing_member:
                            # Insert new member
                            cursor.execute(
                                "INSERT INTO user (name, login, hash, badge_id, email, active) VALUES (%s, %s, %s, %s, %s, %s)",
                                (
                                    name,
                                    None,
                                    'na',
                                    card,
                                    'noemail@pikespeakmakerspace.org',
                                    1
                                )
                            )
                            new_members_count += 1
                            logger.info(f"Added new member: {name} with card {card}")
                
                # Commit the transaction
                connection.commit()
                logger.info(f"Member sync completed successfully. Added {new_members_count} new members.")
             
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                
            finally:
                if 'connection' in locals() and connection.open:
                    connection.close()
                    logger.info("Database connection closed")
                    
        except Exception as e:
            logger.error(f"Error in sync_members: {str(e)}")
            print(f"Error syncing members: {str(e)}")