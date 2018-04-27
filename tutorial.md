# Building an Python-Powered Web Database for a Biological Dataset


## Introduction

TODO


## Vocabulary

For illustrative purposes, consider the following tables, which contain data that can be modeled in a database:

### Table 1: Specimens
<table>
<tr>
	<th>Specimen Number</th>
	<th>Date Collected</th>
	<th>Species Name</th>
	<th>Site Name</th>
</tr>
<tr>
	<td>1</td>
	<td>2018-04-23</td>
	<td><em>Pseudacris crucifer</em></td>
	<td>Round Pond</td>
</tr>
<tr>
	<td>2</td>
	<td>2018-04-26</td>
	<td><em>Lithobates pipiens</em></td>
	<td>Shallow Swamp</td>
</tr>
<tr>
	<td>...</td>
	<td></td><td></td><td></td>
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
A relation is a collection of similar items, with a (mostly) consistent set of **fields** (see below). Analogous to a **table** or **sheet** in a spreadsheet. For example, in database lingo, the Specimens and Sites tables described above could be called **relations**.

### Field
A field is some property of an item in the database. Consider the Specimens relation above, which has four fields: specimen number, date collected, species name, and site name.

In databases, fields **must** be associated with a specific **data type**.

### Data Type
A **data type** describes what types of values a field can hold. For example, an *integer* field can only hold whole numbers (for example `-4324` or `10000002`). The following are common data types used in database definitions:



## Preparing the Dataset

Writing Notes:
* Easier if the metadata is clearly defined
* Avoiding data transformations is good to avoid hidden data corruption
* Consistent formats are ideal for reliable importing
* Know your data! Timezones, possible values, future uses
* Unknowns

TODO



## Designing the Database Schema

Writing Notes:
* Avoid data duplication at all times!
* Use additional relations
* Relationships: one-one, one-many, many-many
	* ADVANCED: Attaching information to relationships
* Which field types to use?

TODO

### Defining Relations

Writing Notes:
* Primary keys
* When to split apart relations
* When to group relations

TODO

### On "Relational" Databases

TODO

### Common Data Types for Fields

#### Integer Fields
Integer fields can store whole numbers within a certain range, typically defined by the specific database software being used. Most databases support integers between `−9 223 372 036 854 775 808` and `9 223 372 036 854 775 807`. These limits may seem arbitrary, but are a result of the underlying representation of this data type (which will not be touched on).

#### Floating-Point Number Fields

TODO

**Warning!** TODO

#### Decimal Number Fields

TODO

#### Variable Character Fields (So-Called `VARCHAR`s)
Variable character fields can store a *limited* number of text characters. When defining these fields, a maximum number of characters, `n`, is passed in, which gives an upper bound on the length of the text which can be stored in these types of fields.

For example, a `VARCHAR(10)` field can store the text `Hello` (5 characters) or `Hello Mike` (10 characters), but **cannot** store the text `Hello Allan`, since it is 11 characters.

#### Text Fields

TODO

#### Django's GIS Types

DOES THIS GO HERE?
TODO


### Further Restricting Possible Field Values

TODO


### Balancing Future Expandability and Restrictiveness

TODO

#### When to Create Secondary Fields

TODO



## Modeling the Schema in Python with Django

TODO


## Importing the Dataset Automatically

TODO

### Making Values Consistent

TODO

### Parsing Values with Regular Expressions

TODO



## Hosting the Database on a Server

TODO
