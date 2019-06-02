import asyncio
import random
import uuid

import aiosqlite


def create_connect():
    return aiosqlite.connect('db.sqlite')


async def make_table():
    sqls = [
        '''CREATE TABLE IF NOT EXISTS "users" ( 
        `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
        `battery` INTEGER, 
        `host` TEXT, 
        `connected_host` TEXT, 
        `is_online` INTEGER, 
        `gps` TEXT, 
        `phone_number` TEXT, 
        `mac_address` TEXT, 
        `distance` INTEGER,
        `active`	INTEGER DEFAULT 1)'''
    ]

    async with create_connect() as db:
        for sql in sqls:
            cursor = await db.execute(sql)
            await cursor.close()

        await db.commit()


async def update_or_insert_user_info(data: dict):
    sql = "select id from users where users.mac_address = ?;"
    pk = None
    async with create_connect() as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(sql, (data.get('id'),)) as cursor:  # type: aiosqlite.Cursor
            row = await cursor.fetchone()
            if row:
                pk = row['id']

        if pk:
            sql = 'UPDATE `users` SET `battery`=?, host=?, connected_host=?, is_online=?, gps=?  WHERE `id`=?;'
            await db.execute(sql, (
                data.get('battery', 0), data.get('host', ''), data.get('connected_host', ''),
                data.get('is_online'),
                data.get('gps', '37.495470,127.038855'), pk
            ))

        else:
            sql = 'INSERT INTO `users`(`battery`,`host`,`connected_host`,`is_online`,`gps`,`mac_address`,`distance`,`active`) ' \
                  'VALUES (?,?,?,?,?,?,?,1);'
            await db.execute(sql, (
                data.get('battery', 0), data.get('host', ''), data.get('connected_host', ''),
                data.get('is_online'), data.get('gps', '37.495470,127.038855'),
                data['id'], data.get('distance') if data.get('distance') else random.randint(0, 7)
            ))

        await db.commit()


async def get_all_user_info():
    users = []
    sql = '''SELECT * FROM `users`'''
    async with create_connect() as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(sql) as cursor:
            async for row in cursor:
                users.append({"user_id": row['mac_address'], "distance": row['distance']})

    return users


async def disable_user(user_id):
    sql = 'UPDATE `users` SET `active`=0 WHERE `mac_address`=?;'
    async with create_connect() as db:
        await db.execute(sql, user_id)
        await db.commit()


{
    "type": "update",
    "sequence_id": "ff70a4cd231",
    "id": "01050282038",
    "battery": 100,
    "my_host": "192.168.0.1",
    "connected_host": "192.168.100.12",
    "is_online": False,
    "gps": "37.495470,127.038855"
}
'''
    async with aiosqlite.connect(...) as db:
        await db.execute('INSERT INTO some_table ...')
        await db.commit()

        async with db.execute('SELECT * FROM some_table') as cursor:
            async for row in cursor:
                ...
                
                
                
                '''

if __name__ == '__main__':
    _loop = asyncio.get_event_loop()


    async def main():
        await make_table()
        async with create_connect() as db:
            return await update_or_insert_user_info({'id': '1'})


    print(_loop.run_until_complete(main()))
