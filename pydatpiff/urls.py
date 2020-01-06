class Urls:
    url = {
        'base'  :'https://www.datpiff.com/',
        'album' :'http://www.datpiff.com',
        'search':'https://www.datpiff.com/mixtapes-search',
        }

    category = {
                "hot":"http://www.datpiff.com/mixtapes/hot",
                "new":"http://www.datpiff.com/mixtapes",
                "top":"http://www.datpiff.com/mixtapes-top",
                "celebrated":"http://www.datpiff.com/mixtapes/celebrated",
                "popular":"http://www.datpiff.com/mixtapes-popular.php",
                "exclusive":"http://www.datpiff.com/mixtapes-exclusive",
                "most download":"http://www.datpiff.com/mixtapes-popular.php?sort=downloads",
                "most listen":"http://www.datpiff.com/mixtapes-popular.php?filter=month&sort=listens",
                "most favorite":"http://www.datpiff.com/mixtapes-popular.php?sort=favorites",
                "highest rating":"http://www.datpiff.com/mixtapes-popular.php?filter=month&sort=rating"
                }

    @staticmethod
    def payload(artist):
        data = {'submit':'MTAxNTUuNzcxNTI5NDEyMzY0MTgwNzEx',
                        'criteria':artist
               }
        return data

