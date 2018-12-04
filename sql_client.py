import mysql.connector
from datetime import datetime

class MySqlClient():
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="104.197.80.146",
            user="cs6400",
            passwd="xx", # please check with me the password
            database="cs6400"
        )

    def get_all_categories(self):
        return self._select("select * from categories")

    def get_latest_items(self):
        mycursor = self.mydb.cursor(buffered=True)
        mycursor.execute("""select it.`*`, y.imageurl
                            from items it
                                inner join users u on it.UserId = u.id
                                left join (
                                    select itemid, min(id) as min_id
                                    from images i
                                    group by itemid
                                ) x on it.Id = x.itemid
                                left join images y on y.id = x.min_id
                            limit 20;""")
        result = []
        columns = tuple( [d[0] for d in mycursor.description] )
        for row in mycursor:
            result.append(dict(zip(columns, row)))
            
        return result

    def check_username(self, username):
        result = self.get_user_by_name(username)
        return len(result)

    def register(self, username, password):
        try:
            cursor = self.mydb.cursor()
            cursor.execute('''Insert into users (Name, password, Email, JoinTime) values (%s, %s, %s, %s)''', (username, password, '', datetime.now()))
            self.mydb.commit()
        except Exception as e:
            print(e)
            return 0
        return cursor.rowcount

    def get_user_by_name(self, name):
        result = self._select("SELECT * from users where name = '%s';"%name)
        if len(result) > 0:
            return result[0]
        else:
            return None

    def get_user_by_username_password(self, name, password):
        result = self._select("SELECT * from users where name = '%s' and password = '%s';" % (name, password))
        if len(result) > 0:
            return result[0]
        else:
            return None

    def add_image_to_item(self, item, link):
        cursor = self.mydb.cursor()
        cursor.execute("insert into images (itemid, imageurl) values (%s, '%s');"%(item, link))
        self.mydb.commit()

    def get_images_by_item_id(self, item_id):
        return self._select("select * from images where itemid = %s order by id"%item_id)

    def create_item(self, userid, data):
        cursor = self.mydb.cursor()
        query = """insert into items (UserId, Name, Description, Price, Likes, Location, TradeMethod, Status, CreatedOn)
                          values(%s, '%s', '%s', %s, %s, '%s', '%s', %s, '%s')"""%(userid, data["Name"], data["Description"], data["Price"], 0, data["Location"], data["TradeMethod"], 0, datetime.now())
        cursor.execute(query)
        self.mydb.commit()
        result = self._select("select * from items where userId = %s order by id desc limit 1;" % userid)
        return result

    def add_categories_to_item(self, item_id, categories):
        cursor = self.mydb.cursor()
        l = []
        for category in categories:
            l.append("(%s, %s)"%(item_id, category, ))
        query = "insert into item_category (itemid, categoryid) values " + ",".join(l)
        print(query)
        cursor.execute(query)
        self.mydb.commit()

    def update_item(self, data):
        cursor = self.mydb.cursor()
        query = """update items set Name='%s', Description='%s', Price=%s,
                    Location='%s', TradeMethod='%s'
                    where Id = %s
                    """%(data["Name"], data["Description"], data["Price"], data["Location"], data["TradeMethod"],data["Id"])
        cursor.execute(query)
        self.mydb.commit()
        
    def delete_categories(self, item_id, categories):
        cursor = self.mydb.cursor()
        query = """delete from item_category where itemid = %s and categoryid in (%s)"""%(item_id, ",".join(categories))
        cursor.execute(query)
        self.mydb.commit()

    def get_item_by_id(self, item_id):
        return self._select("select * from items where id = %s;" % item_id)

    def get_latest_items_by_category(self, item_id):
        return self._select("""select *
                               from items as i INNER JOIN item_category as j
                               ON i.id = j.itemid
                               where j.categoryid = %s;""" % item_id)
                               
    def get_item_categories(self, item_id):
        return self._select("""select categoryid
                             from item_category
                             where itemid = %s"""%item_id)

    def get_images_by_itemid(self, itemid):
        return self._select("select * from images where itemid = %s"%itemid)

    def delete_image_by_imageid(self, imageid):
        cursor = self.mydb.cursor()
        cursor.execute("delete from images where id = %s"%imageid)
        self.mydb.commit()

    def like_item(self, user_id, item_id):
        cursor = self.mydb.cursor()
        cursor.execute("insert into item_like (itemid, userid) values (%s, %s)"%(item_id, user_id))
        self.mydb.commit()

    def get_item_likes(self, user_id, item_id):
        cursor = self.mydb.cursor()
        return self._select('''
                                select count(1) as Total, count(u.id) as mycount
                                from item_like il
                                    left join users u on il.userid = u.id
                                where il.itemid = %s and u.id = %s
                            '''%(item_id, user_id))

    def make_comment(self, user_id, item_id, message):
        cursor = self.mydb.cursor()
        cursor.execute("insert into comments (userid, itemid, content, createdon) values (%s, %s, %s, %s)"%(user_id, item_id, content, datetime.now()))
        self.mydb.commit()

    def get_my_items(self, user_id):
        # return self._select("select * from items where userid = %s order by createdon desc"%user_id)
        mycursor = self.mydb.cursor(buffered=True)
        mycursor.execute("""select it.`*`, y.imageurl
                            from items it
                                inner join users u on it.UserId = u.id
                                left join (
                                    select itemid, min(id) as min_id
                                    from images i
                                    group by itemid
                                ) x on it.Id = x.itemid
                                left join images y on y.id = x.min_id
                            where it.UserId = %s;"""%(user_id))
        result = []
        columns = tuple( [d[0] for d in mycursor.description] )
        for row in mycursor:
            result.append(dict(zip(columns, row)))
        return result

    def get_search_items_by_name(self,searchitem):
        mycursor = self.mydb.cursor(buffered=True)
        pattern = "%" + searchitem + "%"
        mycursor.execute("""select it.`*`, y.imageurl
                            from items it
                                inner join users u on it.UserId = u.id
                                left join (
                                    select itemid, min(id) as min_id
                                    from images i
                                    group by itemid
                                ) x on it.Id = x.itemid
                                left join images y on y.id = x.min_id
                                where it.name like '%s';"""%(pattern))
                            
        result = []
        columns = tuple( [d[0] for d in mycursor.description] )
        for row in mycursor:
            result.append(dict(zip(columns, row)))
        return result

    def get_my_favourites(self, user_id):
        return self._select("select i.* from items i inner join item_like l on i.id = l.itemid where l.userid = %s order by l.id desc"%user_id)

    def get_item_by_category_id(self, category_id):
        return self._select("""select * from items i inner join item_category ic on i.id = ic.itemid where ic.categoryid = %s order by i.id desc"""%category_id)
        # mycursor = self.mydb.cursor(buffered=True)
        # mycursor.execute("""select ic.`*`, y.imageurl
        #                     from item_category ic
        #                         inner join items i on ic.itemid = i.id
        #                         left join (
        #                             select itemid, min(id) as min_id
        #                             from images i
        #                             group by itemid
        #                         ) x on i.Id = x.itemid
        #                         left join images y on y.id = x.min_id
        #                     where ic.categoryid = %s;"""%(category_id))
        # result = []
        # columns = tuple( [d[0] for d in mycursor.description] )
        # for row in mycursor:
        #     result.append(dict(zip(columns, row)))
        # return result

    def _select(self, sql):
        mycursor = self.mydb.cursor(buffered=True)
        mycursor.execute(sql)
        return self._parse_result(mycursor)

    def _parse_result(self, mycursor):