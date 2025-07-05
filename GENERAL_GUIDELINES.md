# General Prolog Guidelines

## Development environment

We highly and strongly recommend using a proper IDE for developing Prolog code. The best we know so far today is [Visual Studio Code (VSCode)](https://code.visualstudio.com/) with extension [VSC-Prolog](https://github.com/arthwang/vsc-prolog). You will get syntax highlighting, snippets and completion suggestions, hover information, grammar linter (fundamental!), and many many other features for proper development.

## Loading files

Unless specified otherwise, one should not load a database in the same file where the reasoning rules are located. For example, if we have a database of Uni courses in file `courses.pl` and a Prolog reasoning system to reason about program plans named `uni_programs.pl`, then the latter should NOT load `courses.pl` itself, as it should work with any course database possible. 

Instead, to test it one can consult both as follows:

```prolog
-? ['courses.pl'].
-? ['uni_programs.pl'].
```

Alternatively, one can design a single program `main.pl` with:

```prolog
:- ['courses.pl'].
:- ['uni_programs.pl'].
```

and just consult `main.pl`.

## Singleton variables

To get more marks and more robust code, we strongly suggest to **avoid singleton variables!** A singleton variable is a variable that only occurs once in the arguments or the body
of a predicate and is thus useless. For example in the following two definitions:

```prolog
calculate(X, Y, Z) :- Z is X+2.
```
Here `Y` is a singleton variable, and should be prefixed by an underscore `_Y` or replaced by an anonymous variable `_`.

Singleton variables make it harder to read the code and can signal a bug, like in the following example:

```prolog
inc(FirstNr, Result) :- Result is Firstnr+1.
```

Here, both `FirstNr`and `Firstnr` will be reported as singleton variables! This is very useful information because it often helps you finding typos, a common source of bugs in Prolog, as shown above (`Firstnr` should have been `FirstNr`).

## Use of `;/2`

It is generally OK to use `;/2` as part of a simple _if-then-else_ construct when the whole logic is simple, for example to set a variable:

```prolog
(<condition> -> Speed = 0 ; Speed = MaxSpeed)
```

This is fine as it only sets `Speed` and has a very simple logic, no complex code is either branch of the "if" construct.

However, code like this one:

```prolog
p(X,Y,Z) :-
 <code A> ; <code B>.
 ```

should instead be written as two separate clauses:

```prolog
p(X,Y,Z) :- <code A>.
p(X, Y,Z):- <code B>.
```

## Documentation

Each predicate you write should have a concise and clear documentation also indicating its mode of usage. You can find plenty of good documentation examples in the SWI-Prolog manual and even help system (e.g., try `help(append)`).

For **documentation style** similar to JavaDoc, refer to [SWI-Prolog Source Documentation](https://www.swi-prolog.org/pldoc/doc_for?object=section(%27packages/pldoc.html%27)).

## Strings as atoms

In Prolog, any string starting with capital letter is considered a variable. So, to represent a string a name like "Alan Turing" you have two options:

1. You explicitly single quote it, e.g., `'Alan Turing'` to indicate the whole name is an atom.
2. You use snake case notation, e.g., `alan_turing`.

Note that SWI Prolog does include a type String, but is used mostly for I/O operations and where the text does not denote an identifier.

In most cases, you would want to represent the names as _atoms_.

See [this explaination](https://www.swi-prolog.org/pldoc/man?section=string) for more information.


## Indentation

As always, your code should be easy to read. Putting every subgoal on a new line is a good idea.

## Efficiency

Unless specifically stressed, you don't have to go out of your way for optimization purposes. However, the code must aim to be reasonably efficient. You should not be traversing the lists unnecessarily, for example. Basically, without doing crazy tricks, your code should aim to be efficient.

## Duplicate answers

In general, you should eliminate duplicates whenever you can. Sometimes, however, you may not be able to eliminate all duplicates, and that's OK. In each query, you should make a decision as to whether or not it is possible to eliminate duplicates.  Sometimes there are different causes of duplicates, and you can deal with one, but not the other. It is part of the task to figure it out when it is doable and when it is not.

## Style

* Simpler, shorter code is generally best.
* Try to use unification variables when possible; for example `swap([A,B], [B,A]).` rather than `swap(L1, L2) :- L1=[A,B], L2=[B,A].`
* Pick intuitive names for your predicates and arguments.
* good naming convention for a helper predicate used by a predicate `pred` is `pred_aux` (`aux` stands for"auxiliary"). This makes it easier to understand what it is used for.
