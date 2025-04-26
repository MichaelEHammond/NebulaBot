# import sqlite3
# import os

# # DB Connection
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# def create_messages_table():
#     connection = sqlite3.connect(f"{BASE_DIR}\\user_messages.db")
#     cursor = connection.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS user_messages_per_guild (
#             "user_id" INTEGER,
#             "message" STRING,
#             "message_count" INTEGER,
#             "guild_id" INTEGER,
#             PRIMARY KEY ("user_id", "message", "guild_id")
#         )
#     """)
#     connection.commit()
#     connection.close()

# def increase_message_count(user_id: int, guild_id: int):
#     connection = sqlite3.connect(f"{BASE_DIR}\\user_messages.db")
#     cursor = connection.cursor()

#     cursor.execute("""
#         SELECT message_count
#         FROM user_messages_per_guild
#         WHERE user_id = ? AND guild_id = ?;
#     """, (user_id, guild_id))
    
#     result = cursor.fetchone()

#     if result is None:
#         cursor.execute("""
#             INSERT INTO user_messages_per_guild (user_id, message_count, guild_id)
#             VALUES (?, 1, ?);
#         """, (user_id, guild_id))
#         connection.commit()
#         connection.close()
#         return 1
    
#     cursor.execute("""
#         UPDATE user_messages_per_guild
#         SET message_count = ?
#         WHERE user_id = ? AND guild_id = ?;
#     """, (result[0] + 1, user_id, guild_id))
#     connection.commit()
#     connection.close()
#     return result[0] + 1