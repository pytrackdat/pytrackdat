# Building Python-Powered Web Databases for Biological Datasets


## Introduction

When building a dataset, a common early step is to design and populate a
spreadsheet. This lets a researcher organize data entries based on their
common measurements, keep data consistent, and perform analysis on the data.

Spreadsheets, however, have downsides when datasets become large, collaborative
projects as is often the case in modern projects. Editors may have different
ideas about what aspects of a spreadsheet mean if column definitions are not
clearly defined; multiple versions can lead to **multiple sources of "truth"**
and conflicting data (meaning it is not clean where the canonical master
dataset actually resides, if there is one at all). Other, more insidious issues
may also appear, such as inconsistencies in measurement systems and
nomenclature.

Databases provide a solution to this problem by providing a highly structured,
multi-user system for organizing, searching, and filtering data. They do this
by requiring the database architect to construct a **schema**; a clear
definition of data tables and relations that fully encapsulate the possible
values and relationships of the dataset.

Notes:
* databases are often used in (INSERT COMMON DATABASE SYSTEM TYPES HERE) to ...

### The Value of Structure

TODO


## Vocabulary and Concepts Used

TODO: Purpose of the section

For illustrative purposes, consider the following tables, which contain data
that can be modeled and stored in a database:

### Table 1: Specimens
<table>
<tr>
	<th><span style="text-decoration: underline;">Specimen Number</span></th>
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
	<th><span style="text-decoration: underline;">Site Name</span></th>
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

### Primary Key
A **primary key** is a field of a relation which serves as a **unique
identifier** for the tuple in question. These are especially useful when
referencing a different tuple from within a tuple while avoiding needless
data duplication.

Primary keys can be divided into two categories: natural keys and artificial
keys.

**Natural keys** are fields which describe some "real-world" property
of whatever is being described by the tuple.

**Artificial keys** are fields which are explicitly designed as an otherwise
meaningless number or string of alphanumeric characters that uniquely identify
the tuple (and often by extension the actual item) in question.

For example, in the two tables described above, the "Specimen Number" field
of Table 1 could be used as an artificial key and the "Site Name" field of
Table 2 could be used as a natural key, assuming that no two sites will have
the same English name.

### Tuple
**Also known as:** Row, entity

TODO

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

By convention in Python, methods' names are in all lowercase letters, with words
separated by underscores.

### Class *(General Programming)*

In programming, a class describes a *type* of data. It provides an abstract
template of sorts for modeling objects that share common properties.

Objects that use this template are called **instances** of the class.

Classes can themselves have **member methods**, which are methods that can
be called on instances of the class.

Consider the following class, written again in the Python language, which models
the data described in Table 1 above:

```python
class Specimen:
    def __init__(self, specimen_no, date_collected, species_name, site_name,
                 sex, collectors):
        self.specimen_no = specimen_no
    	self.date_collected = date_collected
    	self.species_name = species_name
    	self.site_name = site_name
    	self.sex = sex
    	self.collectors = collectors

    def get_species_with_excitement(self):
        return self.species_name + "!!!"  # Returns the species with excitement!

```

> #### Class Naming Conventions
> By convention, class names in Python start with a capital letter.
> Multiple-word class names are written without any separators by starting the
> next word with a capital letter, like this: `ExampleClassName`.

Within the class, there are two member methods defined. The first one, defined
with the name `__init__`, is a special method called a **constructor**. Passed
into it is any data that the new instance should have as properties, or values
that are used to set the properties of the instance in some other way.

We can create an instance of the `Specimen` as follows:

```python
a_frog = Specimen(1, "2018-04-23", "Pseudacris crucifer", "Round Pond", "M",
                  "Mike, Jim")
```

> #### Don't Worry!
> When making the database with Django, this type of code will mostly be
> automatically handled by Django, including the definition of any
> constructors. Except for the fundamental concepts of a class and an
> instantiation of a class, everything here is just to supplement
> understanding of how Django is handling the data and how it relates to the
> concepts of relations and tuples described above.
>
> For more advanced Django usage and customization of the database, these
> concepts can be applied more directly.

Notice that the values we pass in to the *instantiation* method of the class
correspond with the parameters of the constructor method. The `__init__` method
is not called directly by name; instead, the name of the class is used.

Inside the constructor method, there are various lines setting the values of
variables preceded by `self.`. The `self` variable (passed automatically into
any member method as the first parameter of the method) is how the instance
can refer to **itself**. This allows it to set variables within *itself* to
the values of the parameters passed into the constructor method.

We can access the values of the parameters set in the `a_frog` instance defined
above as follows, in this case with the `collectors` variable in the instance:

```python
# Print the collectors property of the a_frog object:
print(a_frog.collectors)
```

We can also call the other method we defined on the object, which calculates
its value based on properties of the instance accessed within the method itself:

```python
# Call the member method we defined and print the returned result:
print(a_frog.get_species_with_excitement())
```

TODO: finishing notes?



## Preparing the Dataset

Writing Notes:
* Easier if the metadata is clearly defined
	* including relations between sheets/tables
* Avoiding data transformations is good to avoid hidden data corruption
	* it's difficult to think of all edge cases (examples? / logic errors)
* Consistent formats are ideal for reliable importing
* Know your data! Timezones, possible values, future uses
* Unknowns
	* different types of unknowns (this has already been mentioned?)

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

In a scientific setting, it is often important to keep track of significant
figures, and have decimals be represented accurately and with little data
loss. While these standards are relatively easily met with a normal spreadsheet,
there can be suprisingly subtle issues representing decimals with standard
data types provided by the database software, and indeed in most programming
languages in general.

The Django framework provides both floating-point and fixed-precision decimal
data types for fields. These both have disadvantages; the fixed-precision
decimal data type provided requires the database designer to specify the
**exact** precision (length) of the parts of the number both before and after
the decimal, so the field can only represent a fixed significance with a
relatively low maximum value.

Floating points have the advantage of being able to represent a *huge* range
of numbers, but do not have a concept of precision in the same way. For example,
if the value ends in `.00`, it will get truncated to a whole number.

Floating points also have more subtle accuracy issues, resulting in slighty
odd representations of seemingly simple numbers. These issues are difficult
to control and more nuanced.

> ##### The Issue with Floating Points
> Floating point numbers are a method used by most programming languages to
> represent fractional numbers, e.g. `0.2` or `-432.542668`. However, due to
> the internal representation of these numbers, they aren't always entirely
> precise in reflecting the "correct" value of their assigned number.
> For example, consider the expression `4 - 3.2`. This obviously evaluates to
> `0.8`. However, when the expression is evaluated using Python, the results
> are suprising:
> ```python
> print(4 - 3.2)
> 0.7999999999999998  # Result of the above print
> ```
> This is obviously not correct! This is an example of a
> **floating-point error**. It is easy to see how this can lead to subtle issues
> in the dataset which may misrepresent the values originally input.

However, if it is not particularely important to store the *exact* value of
a measurement, floating points offer a good, widely supported and compact
representation for a wide range of numbers. If a fixed level of precision makes
sense for the field, decimal fields offer better accuracy with the trade-off
of having to make a decision on precision level beforehand.

Precise decimal fields get significantly more complex to manage if the level of
significant figures varies measurement-to-measurement. For example, multiple
different instruments may be used to collect the same type of reading depending
on the item. One may read to one deciman point, and another to two.

##### Potential Solution to Multiple Precision Levels: A Second Field

If significant figures are important to a field, a second field can be
introduced which stores auxiliary metadata about the actual value in question.
This field can store either the instrument type or the *actual* decimal
precision of the value in the primary field. In the first case, additional
information should be recorded elsewhere about what precision the instruments
in question can achieve. In both cases, the decimal data type of the primary
field should be able to store the maximum precision achievable for that
particular measurement.


#### Problem: Units

Databases have no way of specifying a "unit" for a particular field. It is up
to the researcher to make sure units are kept track of for given measurements,
and that all units in the data files prior to database import are in consistent
units.

##### "Solution": Consistent Units in Data Prior to Import, with Documentation

Before importing data, as mentioned above, make sure all data are in standard
units. The bare minimum for this is within columns, but it is also helpful
to keep measurements in consistent units (or at least systems) across columns.

This can either be documented on a per-field basis in a separate metadata file
or by naming the columns in a way which incorporates unit suffixes, for example
instead of calling a field `length` calling it `length_mm`. This has the benifit
of storing unit information without keeping track of any separate files, but
the downside of a more verbose and less readable field name.

##### Programmatically Cleaning Up Units

If a dataset is particularly large, it may be difficult to fix unit
consistency issues by hand. It is possible to programmatically detect and
interconvert units during the data import process, assuming prefixes are
consistent within the dataset and, if units are left off, there is a consistent
default unit to defer to or simple rules to follow to decide what unit
the measurement has.

The process of doing this interconversion is covered below in the
"Importing the Dataset Automatically" section.


### Step 2: Define a Consistent Data Format

* Sane field names
	* lowercase, underscore separated, describe the data, no redundant info
* Same fields for multiple sheets with the same type of data
	* i.e. use consistent field names across
* Define data types, significant figures (from instrumentation), ... ????

TODO


### Step 3: Simplify and Deduplicate Data

* Don't have anything except primary keys in more than one place
	* Only use primary keys for referencing rows from other tables
* Exactly one row in a spreadsheet per instance
* TODO: where to talk about primary keys?

TODO



## Designing the Database Schema

Writing Notes:
* Avoid data duplication at all times!
	* if one field can be calculated from others (!!! not talked about yet),
	  can use Django / programming / display to automatically calculate
* Use additional relations
* Relationships: one-one, one-many, many-many
	* ADVANCED: Attaching information to relationships
* Which field types to use?
* Combine multiple sheets with the same "type" of data
	* For example, 2017 specimens, 2016 specimens:
	* Make fields consistent, possibly combine sheets and just add a year field

TODO

### General Principles

The following are rules that should typically be followed when designing a
database in order to ensure maximum data integrity and expandibility.

TODO

#### Avoid Data and Relationship Duplication

TODO

#### Use Consistent Relation and Field Names

TODO

#### TODO: More...

TODO


### Defining Relations

Writing Notes:
* Primary keys
* When to split apart relations - difficult boundary
* When to group relations - see above with 2017/2016 specimens

TODO

#### Primary Keys

Primary keys have been defined in the above Vocabulary and Concepts section.
They uniquely identify a tuple within the relation; and by extension are often
used to identify the physical entity (if there is one) being modeled in the
relation.

Each relation defined should have **exactly one** primary key. They can be
either artificial or natural keys. It should be noted which field is the
primary key, and whether or not it is a natural key.

When designing an artifical key, a simple integer field which auto-increments
(database software will do this automatically with the correct setup) is the
most popular choice. A downside to this, apart from the inherent downside of
having an artifical key, is a tendency for human readers to assign more
meaning to the key than it should contain. Despite typically being a seqential,
increasing number, a numerical key of `42` **does not** necessarily represent
the 42<sup>nd</sup> entry in the database chronologically. The order can be
altered by deleting records, and in fact relations should not be considered as
having any inherent order at all by default.

> ##### Aside: Ordering Tuples in a Relation
> If chronological ordering of tuples is desired, an additional field can be
> added. Typically, this would take the form of a date field called something
> like `date_created`, which would be set exactly once when the object is
> created. Then, the tuples can be sorted by their creation date to give a
> chronological order.

If not using this auto-incrementing integer method, there are some
guidelines that should usually be followed when designing artifical keys:

TODO

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


### Installing Django

TODO


### Using the Terminal to Navigate the Computer

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


### Basic Setup

TODO

Writing Notes:
* We need to enable timezone awareness...


### Transforming the Database Design into Python Code with Django's Models

TODO

### Database Systems, Schemas, and Migrations

TODO

#### Calculating Values On-The-Fly

Notes:
* can calculate things from other fields (ex. percentages) without needing to
	manually input them (prone to errors!)

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
