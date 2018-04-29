# Building Python-Powered Web Databases for Biological Datasets


## Introduction

TODO

### The Value of Structure

TODO


## Vocabulary

For illustrative purposes, consider the following tables, which contain data
that can be modeled and stored in a database:

### Table 1: Specimens
<table>
<tr>
	<th>Specimen Number</th>
	<th>Date Collected</th>
	<th>Species Name</th>
	<th>Site Name</th>
	<th>Sex</th>
	<th>Collectors</th>
</tr>
<tr>
	<td>1</td>
	<td>2018-04-23</td>
	<td><em>Pseudacris crucifer</em></td>
	<td>Round Pond</td>
	<td>M</td>
	<td>Mike, Jim</td>
</tr>
<tr>
	<td>2</td>
	<td>2018-04-26</td>
	<td><em>Lithobates pipiens</em></td>
	<td>Shallow Swamp</td>
	<td>F</td>
	<td>Jim, Louise</td>
</tr>
<tr>
	<td>...</td>
	<td></td><td></td><td></td><td></td><td></td>
</table>

### Table 2: Sites
<table>
<tr>
	<th>Site Name</th>
	<th>Longitude</th>
	<th>Latitude</th>
	<th>Comments</th>
</tr>
<tr>
	<td>Round Pond</td>
	<td>TODO</td>
	<td>TODO</td>
	<td>Mostly surrounded by fields</td>
</tr>
<tr>
	<td>Shallow Swamp</td>
	<td>TODO</td>
	<td>TODO</td>
	<td>Forested area</td>
</tr>
</table>

### Relation
***Also known as:** Entity set, table*

A relation is a collection of similar items, with a (mostly) consistent set of
**fields** (see below). Analogous to a **table** or **sheet** in a spreadsheet.
For example, the Specimens and Sites tables described above, when translated
into database definitions, will be called **relations**.

### Field
***Also known as:** Attribute, property*

A field is some property of an item in the database. Consider the Specimens
relation above, which has four fields: specimen number, date collected, species
name, and site name.

In databases, fields **must** be associated with a specific **data type**.

### Data Type
***Also known as:** Type*

A **data type** describes what types of values a field can hold. For example,
an *integer* field can only hold whole numbers (for example `-4324` or
`10000002`).

### Null Value
A **null** value is a database's way of representing a missing value of an
item's field. For example, a blank cell or a "N/A" in anotherwise numeric column
in a spreadsheet could be represented as `NULL` in the database.

These values are not always a good substitute for any missing value; there are
associated usage issues that can pose problems for data integrity.

### Method *(General Programming)*
***Also known as:** Function*

In programming, a method is a self-contained piece of code which takes in
input parameters and returns a value calculated with these parameters and,
optionally, other external data.

The purpose of a method is to reduce code duplication and combine similar bits
of logic used in multiple places in the program by containing it to one named
and isolated piece of code.

For example, the following is a definition of a method that calculates the sum
of two numbers in the Python programming language:

```python
def sum_of_two(first, second):
    return first + second
```

The `return` statement here tells the program what value the method will give
back to any code which **calls** the method, i.e. uses the resulting value
in other calculations.

This method could then be used to print out the sum of `5` and `6` to the screen
with another piece of code:

```python
print(sum_of_two(5, 6))  # Prints "11" to the screen
```

The part of the line here preceded by a `#` is a **comment**, which can be
used to clarify and otherwise explain code for future readers.

### Class *(General Programming)*

TODO



## Preparing the Dataset

Writing Notes:
* Easier if the metadata is clearly defined
* Avoiding data transformations is good to avoid hidden data corruption
* Consistent formats are ideal for reliable importing
* Know your data! Timezones, possible values, future uses
* Unknowns

Creating a database becomes much easier when the data that will be stored in the
database has a clearly-defined format, with well-understood value ranges for all
fields.

It is important to understand and account for extreme cases in the database,
since these outliers are what needs considering most when choosing how to model
a particular dataset.

TODO


> ### Aside on Inconsistent Data
>
> A major problem in database design and day-to-day usage is
> **inconsistent data**. In some cases, these inconsistencies can be fixed by a
> human – for example, formatting inconsistencies can often trivially be fixed
> with find-and-replace operations in a spreadsheet.
>
> However, this issue can much worse if data gets coerced into incorrect values
> in a manner that is **indestingishable** from TODO


### Step 1: Know Your Data

The most important consideration, when preparing to create a database for a
specific dataset, is to know as much as possible about the data as possible.
This information is often kept track of in metadata files, and will greatly
assist in translating more loosely-structured data into the rigid structures
required by a database.

The following are useful and potentially subtle factors that should be
understood prior to creating a database:

#### Problem: Date/Time Storage and Timezones

In many cases, timezones are impled in data files. However, in databases, which
explicitly store timezones, this can result in incorrect data. For example, the
database may assume all time is passed in as `GMT` (Greenwich Mean Time),
whereas it was implied to users of the dataset that it was in EST/EDT. In this
case, times will be incorrect by an offset of 4-5 hours depending on time of
year. However, it still appears that these are correct dates – they just don't
correspond with what dates were *intended* by the datasets' authors.

This is further complicated by Daylight Savings Time – is a given piece of data
in EST or EDT? This can be inferred from the date itself, but doing post-hoc
operations on a database can be a recipe for disaster.

For these reasons, it is important to clearly define what timezone(s) your data
is passed in as, and what it should be stored as.

##### Solution – Using GMT Internally and Transforming as Needed

One common solution to this issue is to store all times in the database in GMT,
which is a universally-recognized standard timezone.

This still needs to be thoroughly documented for anyone using the dataset.
In Django's case, the timezones can be **internally** stored as GMT,
but will be automatically translated into the user's **local** timezone when
displaying it [1]. This feature must be manually enabled, but is highly
suggested.

While this mechanism is useful, all users should be aware of this internal
storage mechanism – if the raw database data is viewed, it will be in GMT time.

#### Problem: Missing, Unknown, and Unknowable Values

Missing data are a part of almost any real-word dataset. It is useful to
awknowledge this inevitability when designing databases in order to accurately
represent the missing data – the question that must be asked here is
*in which way* is the data "missing"?

Consider the following scenarios which could lead to a blank cell or
"N/A" in a spreadsheet cell, in some way representing missing data:

1. The data was not recorded by accident, and will never be available (since,
	for example, the ability to take the measurement has been lost).
	TODO: Concrete Example?
2. The data was not recorded yet, but can be later filled in. For example, one
	could go back and take the measurement after the fact. TODO: Concrete ex?
3. The data was not recorded because it doesn't make sense (i.e. is not
	applicable) given the other values in the column.

Now, all three of these could be represented as a `NULL` or blank value in a
database. However, by doing this we may be **losing information** about the
actual meaning behind a blank field. An "N/A" has different semantic meaning
than a blank cell in a spreadsheet, but in the case of a restricted field
in a database, such as an integer or date field, there are no options for values
except an integer or a `NULL`.

Even if this information is stored in a comment in the spreadsheet or database,
or if the reason for the missing data is implicitly known, it can be useful
to differentiate between these types of missing values. This allows us to query
the database for specific types of missing data, allowing a user to for example
find all items in a database which fit the situation mentioned in case 2 above,
in order to make a list of entries which need further measurements to be taken
to "complete" the entry in the database.

##### Stopgap Solution: A Second Status Field

Consider, now, two fields. The first field, when available, contains the actual
value of the measurement or information. The second field contains the status
of the measurement, which can illuminate the cause of a `NULL` value in the
first field. For example, we can have `length` as the first field, and
`length_status` as the second. This `length_status` field can be restricted
to the following candidate values:

* `valid`
* `missing`
* `unrecorded`
* `not_applicable`

Now, when the first field is `NULL`, a database user can set the second status
field to a value which helps keep track of the cause for the missing data.

> This setup has an **important caveat:** It is up to the database users
> themselves to make sure this value is actually correct. It is possible but
> very difficult to enforce a constraint on a database which prevents the
> status field from reading `valid` if the first field is `NULL`, meaning that
> the burden of correct information is almost entirely on the database
> maintainer(s) without help from the database schema.

#### Problem: Decimal Precision, Significant Figures, and Floating Points

TODO

> ##### The Issue with Floating Points
> TODO

This gets significantly more complex if the level of significant figures varies
measurement-to-measurement. For example, multiple different instruments may be
used to collect the same type of reading depending on the item.

In this case, TODO.

Writing Notes:
* Significant figures
	* Different significant figures????
* Floating-point errors
* Approximation...

TODO

##### Possible Solution: TODO

TODO

#### Problem: Units

Writing Notes:
* Clearly defined units
* Units in cells versus in headers
* Multiple units
	* Cleaning up beforehand vs. programmatically fixing with regex (see below)


### Step 2: Define a Consistent Data Format

* Sane field names
* Same fields for multiple sheets with the same type of data
* Define data types, significant figures (from instrumentation), ... ????

TODO


### Step 3: Simplify and Deduplicate Data

* Don't have anything except primary keys in more than one place
* Exactly one row in a spreadsheet per instance
* TODO: where to talk about primary keys?

TODO



## Designing the Database Schema

Writing Notes:
* Avoid data duplication at all times!
* Use additional relations
* Relationships: one-one, one-many, many-many
	* ADVANCED: Attaching information to relationships
* Which field types to use?
* Combine multiple sheets with the same "type" of data
	* For example, 2017 specimens, 2016 specimens:
	* Make fields consistent, possibly combine sheets and just add a year field

TODO

### Defining Relations

Writing Notes:
* Primary keys
* When to split apart relations - difficult boundary
* When to group relations - see above with 2017/2016 specimens

TODO

#### Primary Keys

Writing Notes:
* Unique identifier
* Typically numeric or if alphanumeric, more "code-like" than english
	* Avoid fully-written sentences etc.
* Don't include useless info – instead of "Specimen 5", use "5"
	within the specimen_id field

TODO

#### Fields

Writing Notes:
* Careful with this vs. vocabulary section – how to distinguish?
* Talk about data types to use -- see below too -- how to distinguish?
* Talk about missing values, referring to previous section

TODO

#### Relationships

Writing Notes:
* One-one, one-many, many-many
* Relationships versus normal fields - when to have a foreign key vs. a normal
	attribute?

TODO

### Common Data Types for Fields

Writing Notes:
* TODO: Discuss null values further???

#### Integer Fields
Integer fields can store whole numbers within a certain range, typically
defined by the specific database software being used. Most databases support
integers between `−9 223 372 036 854 775 808` and `9 223 372 036 854 775 807`.
These limits may seem arbitrary, but are a result of the underlying
representation of this data type (which will not be touched on).

#### Floating-Point Number Fields

TODO

**Warning!** TODO

#### Decimal Number Fields

TODO

#### Variable Character Fields (So-Called `VARCHAR`s)
Variable character fields can store a *limited* number of text characters. When
defining these fields, a maximum number of characters, `n`, is passed in, which
gives an upper bound on the length of the text which can be stored in these
types of fields.

For example, a `VARCHAR(10)` field can store the text `Hello` (5 characters) or
`Hello Mike` (10 characters), but **cannot** store the text `Hello Allan`, since
it is 11 characters.

#### Text Fields

TODO

#### Django's GIS Types

DOES THIS GO HERE?
TODO


### Further Restricting Possible Field Values

Writing Notes:
* Need some introduction to django before this>
* May want to limit ranges - doesn't make sense to have for example -200°C
	* Can prevent typos and give good sanity checks

TODO


### Balancing Future Expandability and Restrictiveness

Writing Notes:
* Contrast to above - have to be careful when restricting values, since in the
	future this may result in re-architecture being needed.

TODO

#### When to Create Secondary Fields

Writing Notes:
* <1 versus 1233 (fisheries issue) -- introducing more fields
* Better representing missing values -- status fields
* ...

TODO


## Introduction to Django

Django is a general-purpose web framework for the Python programming language
that makes it easy to create what are called Create-Read-Update-Delete (CRUD)
applications powered by a database.

When the term "web framework" is used, it in this case means a set of
pre-created methods and classes (if you do not know these terms, see the
Vocabulary section above) for creating a web server which powers a
database-driven "web application", or complex interactive website.

One of its main advantages as a framework for creating database-driven
applications is its built-in administration console, which can automatically
generate a website which acts as a Graphical User Interface (GUI) for managing
data stored in the application.

TODO: Picture of Django Admin Console

For this section, it is useful to have some prior knowledge of the basics of
Python and the command line.

Writing Notes:
* Explain (loosely) web frameworks
* Prior knowledge: python?
* GUI Admin console
* ...

TODO



## Modeling the Schema in Python with Django

TODO

### Introduction

TODO


### Creating a Django Project

TODO

```bash
django-admin startproject my_project_db
```

TODO: Created folder structure explanation


### Creating a Django App

TODO

```bash
python ./manage.py startapp core
```

TODO: Created files


### Setting Up the Basics

TODO

Writing Notes:
* We need to enable timezone awareness...


### Transforming the Database Design into Python Code with Django's Models

TODO

### Database Systems, Schemas, and Migrations

TODO

### Running the Site (for Development Purposes)

TODO



## Importing the Dataset Automatically

TODO

Writing Notes:
* TODO: Figure out django's mechanism for timezone awareness with these
	commands...

### Writing an Import Command for Django

TODO

#### Making Values Consistent

Writing Notes:
* capitalization
* trimming whitespace

TODO

#### Parsing Values with Regular Expressions

Writing Notes:
* units

TODO



## Hosting the Database on a Linux Server

While the database can be ran and accessed locally, as has already been seen,
a lot of the power of a web database is having any collaborator be able to
access it from their own devices using usernames and passwords.


TODO



## References
1. Django Framework Documentation: Time zones.
	https://docs.djangoproject.com/en/1.11/topics/i18n/timezones/
