import reflex as rx
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
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
    movie_rec_array: List[str] = []

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
    # Get a DataFrame from recommend_movies and then extract the 'poster_path' column as a list
        recommended_movies_df = recommend_movies(self.liked_movies, self.disliked_movies, cosine_sim, movies, 5)
        
        # Ensure you're getting the poster paths and converting it to a list
        self.movie_rec_array = recommended_movies_df['poster_path'].tolist()

    def love_title(
        self,
    ):
        print(f"I love {self.current_title} with ID of: {self.current_movie_id}")
        self.liked_movies.append(self.current_title)
        print(self.liked_movies)
        self.randomize_option()
        test = (len(self.liked_movies) + len(self.disliked_movies))
        if test % 5 == 0:
            self.redirect_to_org = True
            yield rx.redirect("/recs")

    def hate_title(
        self,
    ):
        print(f"I hate {self.current_title} with ID of: {self.current_movie_id}")
        self.disliked_movies.append(self.current_title)
        print(self.disliked_movies)
        self.randomize_option()
        test = (len(self.liked_movies) + len(self.disliked_movies))
        if test % 5 == 0:
            self.redirect_to_org = True
            yield rx.redirect("/recs")

    def redirect_to_recs(self):
        print("Redirecting to recommendations page")
        return rx.redirect("/recs")  # Redirect to recommendations page


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
        rx.box(
        rx.heading(
                "Muru | The Movie Guru",
                font_family="Cooper Black", 
                font_size = "9", 
                color = "#4817A4",
                position="absolute", 
                top="50px",
                left="550px"),
            width="100%",
            height="100vh",
            #position="relative",
        ),
        rx.box(
        rx.button(
            rx.icon(tag="heart"),
            "Like",
            color_scheme="green",
            position="absolute",
            bottom="300px",
            right="400px",
            on_click=State.love_title,
        
            ),
            width="100%",
            height="100vh",
            #position="relative",
        ),

        rx.box(
        rx.button(
            rx.icon(tag="thumbs_down"),
            "Dislike",
            color_scheme="crimson",
            position="absolute",
            bottom="300px",
            left="300px",
            on_click=State.hate_title,
        ),
            width="100%",
            height="100vh",
            #position="relative",
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
    foreach_poster(),
    rx.heading(
        "Recommendations Based on Your Likes",
        font_family="Cooper Black",
        font_size = "8", 
        color = "#4817A4", 
        align = "center"
    ),
    #keep going button
    rx.box( 
    rx.button(
        "Keep Going",
        color_scheme="violet",
        position="absolute",
        bottom="600px",
        left="700px",
        on_click=rx.redirect("/")
    ),

    width="100%",
    height="100vh",
        #position="relative",
    ),

    
)   


def poster_maker(poster_path: str):
    return rx.image(src=f"https://image.tmdb.org/t/p/w400{poster_path}")


def foreach_poster():
    return rx.grid(
        rx.foreach(State.movie_rec_array, poster_maker),
        columns="5",
    )
    

# Initialize Reflex App

style = {
    "background": "#d8c0ff",
}

app = rx.App(style=style)
app.add_page(
    index,
    route="/",
    on_load=State.randomize_option,
)
app.add_page(
    recs,
    route="/recs",
    on_load=State.curated_content,
)
