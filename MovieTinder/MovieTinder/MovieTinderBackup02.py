import reflex as rx
from sklearn.metrics.pairwise import cosine_similarity

from .movie_helper import find_row, get_random_movie_id, recommend_movies, movies
cosine_sim = cosine_similarity

config = rx.Config(
    app_name="Movie Tinder",
    frontend_port=3000,
)


class State(rx.State):
    current_title: str = ""
    current_movie_id: int = 0
    liked_movies: list = []
    disliked_movies: list = []
    poster_path: str = ""

    redirect_to_org: bool = False

    def randomize_option(self):
        width = 500
        new_movie_id = get_random_movie_id()
        current_movie_row = find_row(new_movie_id)
        self.current_title = current_movie_row["title"]
        self.current_movie_id = new_movie_id
        base_url = f"https://image.tmdb.org/t/p/w{width}"
        self.poster_path = f"{base_url}{current_movie_row['poster_path']}"
        print("generated a new image"),

    def curated_content(self):
        width = 300
        movie_rec_array = recommend_movies(self.liked_movies, self.disliked_movies, cosine_sim, movies, 5)
        new_movie_id = get_random_movie_id()
        current_movie_row = find_row(new_movie_id)
        self.current_title = current_movie_row["title"]
        self.current_movie_id = new_movie_id
        base_url = f"https://image.tmdb.org/t/p/w{width}"
        self.poster_path = f"{base_url}{current_movie_row['poster_path']}"
        print(f"R: {movie_rec_array}")
        
    def love_title(
        self,
    ):
        print(f"I love {self.current_title} with ID of: {self.current_movie_id}")
        self.liked_movies.append(self.current_title)
        print(self.liked_movies)
        self.randomize_option()
        if (len(self.liked_movies) + len(self.disliked_movies)) % 5 == 0:
            self.redirect_to_recs()  # Trigger redirect

    def hate_title(
        self,
    ):
        print(f"I hate {self.current_title} with ID of: {self.current_movie_id}")
        self.disliked_movies.append(self.current_title)
        print(self.disliked_movies)
        self.randomize_option()

    #def change_redirect(self):
    #    self.redirect_to_org = not self.redirect_to_org

    #@rx.var

    #def url(self) -> str:
    #    return (
            
    #    )
    
    def redirect_to_recs(self):
        print("Redirecting to recommendations page")
        return rx.redirect("/recs/")  # Redirect to recommendations page


def generate_image(
    top: int = 0,
    left: int = 0,
    width: int = 500,
):
    return rx.hstack(
        rx.image(
            src=State.poster_path,
            style={
                "position": "absolute",
                "top": f"{top}px",
                "left": f"{left}px",
                "width": f"{width}px",
            },
        )
    )


def page_content():
    return rx.hstack(
        generate_image(
            top=100,
            left=500,
            width=400,
        ),
        rx.button(
            "I LOVE THIS MOVIEEEE",
            color_scheme="grass",
            on_click=State.love_title,
        ),
        rx.button(
            "I HATE THIS MOVIE",
            color_scheme="ruby",
            on_click=State.hate_title,
        ),
        spacing="20",
    )


def index():
    return rx.vstack(
        page_content(),  # Generate the image and buttons based on the movie ID
        rx.text(
            f"Current Movie: {State.current_title} with ID: {State.current_movie_id}"
        ),  # Display the clicked movie title and ID
    )

def recs():
    return rx.container(
    #heading
    rx.heading(
        "Recommendations Based on Your Likes",
        font_family="Cooper Black",
        font_size = "8", 
        color = "blue", 
        align = "center"
    ),
    #keep going button
    rx.box( 
    rx.button(
        "Keep Going",
        color_scheme="green",
        position="absolute",
        bottom="1000px",
        left="400px",
    ),

    width="100%",
    height="100vh",
        #position="relative",
    ),
    #quit buttton
    rx.box(
    rx.button(
        "Quit",
        color_scheme="red",
        position="absolute",
        bottom="1000px",
        right="400px",
    ),
    
    width="100%",
    height="100vh",
    #position="relative",
)
)


# Initialize Reflex App
app = rx.App()
app.add_page(
    index,
    route="/",
    on_load=State.randomize_option,
)
app.add_page(
    recs,
    route="/recs/",
    on_load=State.curated_content,
)
