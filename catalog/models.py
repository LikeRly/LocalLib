﻿from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
import uuid

class Genre(models.Model):
    name = models.CharField('Наименование', max_length=200, unique=True, help_text='Жанр книги. Например, Фантастика, Детектив, Поэзия и т.п.')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('genre-detail', args=[str(self.id)])


class Language(models.Model):
    name = models.CharField('Наименование', max_length=200, unique=True, help_text='Язык издания книги. Например, Русский, English, 中國 и т.п.')

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """Returns the url to access a particular language instance."""
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField('Наименование', max_length=200, help_text='')
    author = models.ForeignKey('Author', verbose_name='Автор', on_delete=models.RESTRICT, null=True, help_text='')
    summary = models.TextField('О книге', max_length=1000, help_text='')
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='')
    genre = models.ManyToManyField('Genre', verbose_name='Жанр', help_text='')
    language = models.ForeignKey('Language', verbose_name='Язык', on_delete=models.SET_NULL, null=True, help_text='')

    class Meta:
        ordering = ['title', 'author']
        permissions = (("can_change_books_data", "Add, edit, delete books"),)

    def display_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])
    display_genre.short_description = 'Жанр произведения'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Уникальный идентификатор этого экземпляра книги в библиотеке.')
    book = models.ForeignKey('Book', verbose_name='Книга', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField('Штамп', max_length=200, help_text='Информация об экземпляре. Например, издательство, переводчик, год, номер экземпляра в библиотеке')
    due_back = models.DateField(verbose_name='Дата возврата', null=True, blank=True, help_text='Дата ожидаемого возврата книги.')
    borrower = models.ForeignKey(User, verbose_name='Читатель', on_delete=models.SET_NULL, null=True, blank=True, help_text='Читатель, арендующий книгу.')

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('m', 'На оформлении'),
        ('o', 'Выдана'),
        ('a', 'Доступна'),
        ('r', 'В резерве'),
    )

    status = models.CharField('Доступность', max_length=1, choices=LOAN_STATUS, blank=True, default='d', help_text='Статус доступности книги')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('bookinstance-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    first_name = models.CharField('Имя', max_length=100, help_text='')
    last_name = models.CharField('Фамилия', max_length=100, help_text='')
    date_of_birth = models.DateField('Дата рождения', null=True, blank=True, help_text='')
    date_of_death = models.DateField('Дата смерти', null=True, blank=True, help_text='')

    class Meta:
        ordering = ['last_name', 'first_name']
        permissions = (("can_change_authors_data", "Add, edit, delete authors"),)

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
