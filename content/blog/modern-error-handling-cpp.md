+++
title = "Modern Error Handling with C++23"
description = "With the introduction of std::expected, it is finally possible to use error codes in C++ without the usual hassle. This post shows how."
authors = ["Adrian Winterstein"]
date = "2025-04-10"

[taxonomies]
blog-tags=["C++"]

[extra]
comments.host = "mastodon.social"
comments.username = "awinterstein"
comments.id = 114313222274319886
+++

With the introduction of `std::expected` in C++23 and the use of `std::error_code` form C++11, it is finally possible to use error codes in C++ without the usual hassle.

## Using the Modern Error Handling

Let's first see an example of how this could look like. A function that might return an error could be defined like this:

```c++
[[nodiscard]] std::expected<int, std::error_code>
divide(int numerator, int denominator)
{
    if (denominator == 0) {
        return std::unexpected{math_error::division_by_zero};
    }

    return numerator / denominator;
}
```

The `nodiscard` attribute (introduced with C++17) is not required, but I strongly recommend using it, so that the compiler will issue a warning, if the result of a call to the function is not used.

The function can be called then just as shown here:

```c++
// no need for output parameters, the potential error and the
// result can both just be retrieved as a return parameter
const auto result = divide(100, 10);

// check for a valid result to do error handling (expected)
if (!result) {
    // in case of an error, we can directly print the static
    // message, that is connected to the error code, for example
    printf("Failed to calculate: %s", result.error().message());
} else {
    // access the calculated value after checking
    const auto value = result.value();
}
```

But what if we do not actually can handle the error, but want to forward it to our caller? Just return the error in another `std::unexpected`:

```c++
const auto result = divide(100, 10);
if (!result) return std::unexpected{result.error()};

printf("The result was: %i", result.value());
```

Compared to the indeed very nice error handling in Rust, we are missing a bit of syntactical sugar, but the usage pattern is quite close:

```rust
let result = divide(100, 10)?;
print!("The result was: {}", result);
```

## Implementing the Modern Error Handling

Let's see then, how the modern error handling can actually be implemented in C++.
Using `std::expected` is straightforward and could directly be used with your existing error codes if you enabled the C++23 standard on your compiler (see also at [cppreference](https://en.cppreference.com/w/cpp/utility/expected)):

```c++
#include <cstdio>
#include <expected>

// does not need to be an enum class, could also be plain integers
enum class math_error
{
    // the 0 value should always be reserved for 'success'
    division_by_zero = 1,
};

[[nodiscard]] std::expected<int, math_error>
divide(int numerator, int denominator)
{
    if (denominator == 0) {
        return std::unexpected{math_error::division_by_zero};
    }

    return numerator / denominator;
}

int main()
{
    const auto result = divide(100, 10);

    if (!result) {
        printf("Failed to calculate: %s", result.error().c_str());
        return -1;
    }

    printf("The result was: %i", result.value());
}
```

Combining it with `std::error_code` instead of plain error codes, however, has some advantages like:

- multiple enums can be used to define error codes in the application and the linker ensures with the help of `std::error_category` that every error code is unique
- different error code types from different parts of the system can be forwarded by a function, without even needing to know which concrete types are defined
- it can be casted to bool, hence there is no need to compare to some "no error" value
- it contains a human-readable string that can be used for logging, for example

How would the same example look with `std::error_code` then? Let's first define our error codes enum and our custom error category:

```c++
// The enum will all error codes of this part of the software (for one
// specific error category). As many as needed can be defined for
// different subsystems or libraries.
enum class math_error
{
    // the 0 value must be reserved for the 'success' case
    division_by_zero = 1,
};

// The concrete error category does not need to be part of any interface.
// Hence, you would usually define it in an anonymous namespace in an
// implementation file.
namespace
{
    // The error category needs to implement the name() and message()
    // methods to allow for getting human readable information about any
    // given error code later on.
    struct error_category : public std::error_category {
        [[nodiscard]] const char *name() const noexcept override
        {
            return "math_error";
        }

        [[nodiscard]] std::string message(int ev) const override
        {
            switch (static_cast<math_error>(ev)) {
            case math_error::division_by_zero:
                return "Division by zero";
            }

            return "Unknown error";
        }
    };

    // This is how the error codes are ensured to be unique. There must
    // be exactly one instance of each error category defined in your
    // application somewhere in any implementation file. Two error codes
    // are assumed to be in the same category, if the addresses of their
    // categories are identical.
    const error_category the_error_category{};

} // namespace

// This function needs to be implemented to allow for automatic
// conversions of the enum to instances of std::error code. So that you
// only need do 'return math_error:division_by_zero', for example, in a
// function that returns a std::error_code.
std::error_code make_error_code(math_error code)
{
    return {static_cast<int>(code), the_error_category};
}

// The enum must be defined to an error code enum within the std namespace.
// This will lead to the templated conversion functions from an enum value
// to an error code of the std::error_code class to be instantiated for
// this enum class. They will internally call the above defined function
// make_error_code() via argument dependent lookup then.
namespace std
{
    template <>
    struct is_error_code_enum<math_error> : public std::true_type {
    };
} // namespace std
```

There is a bit of boiler-plate code needed, for defining an error category and code. However, this needs to be done only once for every category and you usually won't need many categories. Could be only one for the application code, for example, and one for a 3rd-party dependency. After defining, it can then be used like that:

```c++
#include <cstdio>
#include <expected>
#include <system_error>

// include the error category and code definition from above
// or a corresponding header file

[[nodiscard]] std::expected<int, std::error_code>
divide(int numerator, int denominator)
{
    if (denominator == 0) {
        return std::unexpected{math_error::division_by_zero};
    }

    return numerator / denominator;
}

int main()
{
    const auto result = divide(100, 10);

    if (!result) {
        printf("Failed to calculate: %s", result.error().message().c_str());
        return -1;
    }

    printf("The result was: %i", result.value());
}
```

## Dynamic Memory?

The major disadvantage of `std::error_code` that would prevent me from using it on embedded devices is the use of `std::string` in the interface of `std::error_category` (and also in the implementations of `std::error_code` and `std::error_condition`):

```c++
virtual std::string message(int ev) const = 0;
```

Implementing an error category, would lead to the introduction of dynamic memory via `std::string`, which is usually unwanted in the firmware development. Luckily, the only things that are needed for implementing `system_error` are to provide a `std::error_category` class a `std::error_code` class and optionally `std::error_condition` class. The latter could be left out, if the feature or error conditions are not needed.

All of those classes are quite small and simple, as you could check out in the [STL implementation from the LLVM project](https://github.com/llvm/llvm-project/tree/main/libcxx/include/__system_error), for example. Let's see what we need to implement for a `system_error` without dynamic memory.

{% badge_info(icon=true) %}The source code of a full implementation can be found in my <a href="https://codeberg.org/winterstein/zephyr-example/src/branch/main/application/src/util">Zephyr example repository</a>.{% end %}<br>

We need a slightly different interface for the `error_category` class compared to the version from the <abbr title="Standard Template Library">STL</abbr> to avoid dynamic memory. Its interface would look like this then:

```c++
class error_category
{
public:
    // class uses virtual inheritance → destructor needs to be virtual
    virtual ~error_category() = default;

    // class must not be copied
    error_category() = default;
    error_category(const error_category &) = delete;
    error_category &operator=(const error_category &) = delete;

    // a name must be defined by subclasses
    virtual const char *name() const = 0;

    // define the method for the default error condition, only
    // if you plan to implement and use error conditions
    virtual error_condition default_error_condition(int ev) const;

    // equivalence between error codes and conditions of this category (if error conditions are used)
    virtual bool equivalent(int code, const error_condition &condition) const;
    virtual bool equivalent(const error_code &code, int condition) const;

    // here's the difference to the STL implementation → char* instead of std::string
    virtual const char *message(int ev) const = 0;

    // those operators for equivalence and ordering must be defined
    bool operator==(const error_category &rhs) const;
    bool operator!=(const error_category &rhs) const;
    bool operator<(const error_category &rhs) const;
};
```

Similarly for the `error_code` class, where we also need to replace the usage of `std::string`:

```c++
class error_code
{
public:
    // default constructor must set success value on system_category
    error_code();
    error_code(int value, const error_category &category);

    template <class Enum, typename = typename std::enable_if_t<is_error_code_enum_v<Enum>>>
    error_code(Enum enum_value);

    void assign(int value, const error_category &category);

    template <class Enum, typename = typename std::enable_if_t<is_error_code_enum_v<Enum>>>
    error_code &operator=(Enum enum_value);

    // back to success value on system_category (like default constructed)
    void clear();

    // just getters for the private attributes
    int value() const;
    const error_category &category() const;

    // just to forward call to category().default_error_condition()
    error_condition default_error_condition() const;

    // as for the error_category, the return value needs to be char* instead of std::string
    const char *message() const;

    // operator needs to be implemented to return true on any value != 0
    explicit operator bool() const;

private:
    int value_;
    const error_category *category_;
};
```

As you might have spotted in the interface definitions already, there are two instances of `std::error_category` required to be provided by an implementation: a system category and a general category. For compatibility and for being able to default-construct `error_code` instances, it makes sense to implement those instances as well:

```c++
// implementation of the generic error category
class generic_error_category : public error_category
{
public:
    virtual const char *name() const
    {
        return "generic";
    }
    virtual const char *message(int ev) const
    {
        return strerror(ev);
    }
};

// one instance must be created in an implementation file
const generic_error_category the_generic_error_category{};

// this instance should be returned by a function
const error_category &generic_category()
{
    return the_generic_error_category;
}


// implementation of the system error category
class system_error_category : public error_category
{
public:
    virtual const char *name() const
    {
        return "system";
    }
    virtual const char *message(int ev) const
    {
        return strerror(ev);
    }
    virtual error_condition default_error_condition(int ev) const
    {
        return error_condition(ev, generic_category());
    }
};

// one instance must be created in an implementation file
const system_error_category the_system_error_category{};

// this instance should be returned by a function
const error_category &system_category() noexcept
{
    return the_system_error_category;
}
```

After doing the necessary implementations for the `error_category`, `error_code` and optionally the `error_condition`, the error handling can be used without dynamic memory.

{% badge_info(icon=true) %}Instead of doing your own implementation, feel free to check out what I already implemented in my <a href="https://codeberg.org/winterstein/zephyr-example/src/branch/main/application/src/util">Zephyr example repository</a>.{% end %}<br>
