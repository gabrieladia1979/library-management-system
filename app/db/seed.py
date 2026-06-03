"""Seed the database with sample data for development/demo."""
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.db.database import Base, SessionLocal, engine
from app.models.book import Book
from app.models.loan import Loan
from app.models.user import User


def seed_database():
    """Populate the database with sample books, users, and loans."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if data already exists
    if db.query(Book).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    # Sample books
    books = [
        Book(title="Clean Code", author="Robert C. Martin", isbn="9780132350884",
             genre="Software", published_year=2008, quantity=3, available_copies=2,
             description="A handbook of agile software craftsmanship."),
        Book(title="Design Patterns", author="Gang of Four", isbn="9780201633610",
             genre="Software", published_year=1994, quantity=2, available_copies=1,
             description="Elements of reusable object-oriented software."),
        Book(title="The Pragmatic Programmer", author="David Thomas & Andrew Hunt", isbn="9780135957059",
             genre="Software", published_year=2019, quantity=2, available_copies=2,
             description="Your journey to mastery."),
        Book(title="Cien años de soledad", author="Gabriel García Márquez", isbn="9780060883287",
             genre="Ficción", published_year=1967, quantity=4, available_copies=3,
             description="La saga de la familia Buendía en Macondo."),
        Book(title="El Aleph", author="Jorge Luis Borges", isbn="9780142437889",
             genre="Ficción", published_year=1949, quantity=2, available_copies=2,
             description="Colección de cuentos de Borges."),
        Book(title="Introduction to Algorithms", author="Thomas H. Cormen", isbn="9780262033848",
             genre="Ciencias", published_year=2009, quantity=3, available_copies=3,
             description="The comprehensive textbook on algorithms."),
        Book(title="Rayuela", author="Julio Cortázar", isbn="9788437604572",
             genre="Ficción", published_year=1963, quantity=2, available_copies=1,
             description="Una novela experimental."),
        Book(title="Python Crash Course", author="Eric Matthes", isbn="9781593279288",
             genre="Software", published_year=2019, quantity=5, available_copies=4,
             description="A hands-on, project-based introduction to programming."),
        Book(title="Don Quijote de la Mancha", author="Miguel de Cervantes", isbn="9788420412146",
             genre="Clásicos", published_year=1605, quantity=3, available_copies=3,
             description="La obra cumbre de la literatura en español."),
        Book(title="Refactoring", author="Martin Fowler", isbn="9780134757599",
             genre="Software", published_year=2018, quantity=2, available_copies=2,
             description="Improving the design of existing code."),
    ]
    db.add_all(books)
    db.flush()

    # Sample users
    users = [
        User(name="María González", email="maria.gonzalez@email.com"),
        User(name="Juan Pérez", email="juan.perez@email.com"),
        User(name="Ana López", email="ana.lopez@email.com"),
        User(name="Carlos Rodríguez", email="carlos.rodriguez@email.com"),
        User(name="Laura Martínez", email="laura.martinez@email.com"),
    ]
    db.add_all(users)
    db.flush()

    # Sample active loans
    now = datetime.now(UTC)
    loans = [
        Loan(user_id=users[0].id, book_id=books[0].id,
             loan_date=now - timedelta(days=5), due_date=now + timedelta(days=9)),
        Loan(user_id=users[1].id, book_id=books[1].id,
             loan_date=now - timedelta(days=10), due_date=now + timedelta(days=4)),
        Loan(user_id=users[2].id, book_id=books[6].id,
             loan_date=now - timedelta(days=3), due_date=now + timedelta(days=11)),
        Loan(user_id=users[3].id, book_id=books[3].id,
             loan_date=now - timedelta(days=7), due_date=now + timedelta(days=7)),
        # One returned loan
        Loan(user_id=users[0].id, book_id=books[4].id,
             loan_date=now - timedelta(days=20), due_date=now - timedelta(days=6),
             return_date=now - timedelta(days=8), status="returned"),
    ]
    db.add_all(loans)
    db.commit()
    db.close()
    print(f"Database seeded with {len(books)} books, {len(users)} users, and {len(loans)} loans.")

if __name__ == "__main__":
    seed_database()
