Day 6: Handy Haversacks
================
Jonas Nockert (@lemonad)

I’m using R for this year’s Advent of Code. Learning as I go, which is
quite obvious here : )

It seems like a good idea to start with the given example and work our
way up to the real input. It looks like splitting on the word “contain”
and removing all occurrences of the words “bag” and “bags” is a good
start. \[Eventually, I decided to also remove “no other” as well.\]

``` r
example_input <- trimws("
light red bags contain 1 bright white bag, 2 muted yellow bags.
dark orange bags contain 3 bright white bags, 4 muted yellow bags.
bright white bags contain 1 shiny gold bag.
muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.
shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.
dark olive bags contain 3 faded blue bags, 4 dotted black bags.
vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.
faded blue bags contain no other bags.
dotted black bags contain no other bags.
")

parse_bags <- function(str_or_path) {
  lines <- read_lines(str_or_path)
  bags <- lines %>%
    str_replace_all("(no other bags|bags|bag)", "") %>%
    str_split("contain") %>%
    lapply(trimws, whitespace = "[ \n\r\t\\.]")
}

raw_bags <- parse_bags(example_input)
raw_bags %>%
  head(3) %>%
  kable(
    caption = "Examples of bags and their content",
    col.names = NULL,
    format = "html"
  )
```

<table class="kable_wrapper">
<caption>
Examples of bags and their content
</caption>
<tbody>
<tr>
<td>
<table>
<tbody>
<tr>
<td style="text-align:left;">
light red
</td>
</tr>
<tr>
<td style="text-align:left;">
1 bright white , 2 muted yellow
</td>
</tr>
</tbody>
</table>
</td>
<td>
<table>
<tbody>
<tr>
<td style="text-align:left;">
dark orange
</td>
</tr>
<tr>
<td style="text-align:left;">
3 bright white , 4 muted yellow
</td>
</tr>
</tbody>
</table>
</td>
<td>
<table>
<tbody>
<tr>
<td style="text-align:left;">
bright white
</td>
</tr>
<tr>
<td style="text-align:left;">
1 shiny gold
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>

Not sure if it’s strictly necessary but let’s separate the list into
outer bags and inner bags:

``` r
separate_bags <- function(bags) {
  outer_bags <- bags %>%
    map(1) %>%
    unlist()
  inner_bags <- bags %>%
    map(2)
  list(outer = outer_bags, inner = inner_bags)
}

bags <- separate_bags(raw_bags)
bags$outer %>% head(1)
```

    ## [1] "light red"

``` r
bags$inner %>% head(1)
```

    ## [[1]]
    ## [1] "1 bright white , 2 muted yellow"

So, can we find the bags that hold our *shiny gold* bag directly using
the data structures we’ve set up?

``` r
holds_directly <- bags$outer[
  str_detect(bags$inner, "shiny gold")
] %>%
  unlist() %>%
  unique()
holds_directly
```

    ## [1] "bright white" "muted yellow"

Yes, that looks like the correct answer. Now, it looks like we should do
the same thing for the bag colors contained by those bag colors, etc.

``` r
find_bag_options <- function(color, all_bags) {
  inner_func <- function(colors_to_look_for) {
    matching_bags <- all_bags$inner %>%
      str_split(",") %>%
      lapply(
        function(x) {
          trimws(x, whitespace = "[ \\d]")
        }
      ) %>%
      lapply(
        function(x) {
          x %in% colors_to_look_for
        }
      ) %>%
      lapply(any) %>%
      unlist()
    all_bags$outer[matching_bags]
  }

  # In retrospective, this should have been a recursive solution!
  all_colors <- vector()
  inner <- color
  while (!is_empty(inner)) {
    inner <- inner_func(inner) %>%
      setdiff(all_colors)
    all_colors <- union(inner, all_colors)
  }
  all_colors
}

find_bag_options("shiny gold", bags)
```

    ## [1] "light red"    "dark orange"  "bright white" "muted yellow"

Four (4), like we expected. I think this solution could be refactored to
a much nicer one but let’s try it on the real input:

``` r
raw_bags <- parse_bags("input/december07.input")
bags <- separate_bags(raw_bags)
find_bag_options("shiny gold", bags) %>%
  length()
```

    ## [1] 213

Correct! I might go back and fix things here but, for now, onwards to
part two!

## Part two

Again, we’ll start with the given example, reusing the functions from
part one:

``` r
example_input <- trimws("
shiny gold bags contain 2 dark red bags.
dark red bags contain 2 dark orange bags.
dark orange bags contain 2 dark yellow bags.
dark yellow bags contain 2 dark green bags.
dark green bags contain 2 dark blue bags.
dark blue bags contain 2 dark violet bags.
dark violet bags contain no other bags.
")
raw_bags <- parse_bags(example_input)
bags <- separate_bags(raw_bags)
```

It looks like this forms a tree structure with our shiny gold bag at the
top, followed by 2 dark red bags, etc. This is something we could
recurse down, although it feels like the mention of “topologically
impractical” hints toward a cyclical graph (which is a recurring theme
in previous AoCs). Let’s see:

``` r
recurse <- function(color, all_bags, acc) {
  bag_strings <- bags$inner[bags$outer == color] %>%
    str_split(",") %>%
    unlist() %>%
    trimws()

  # Handle "no other bags", i.e. c("") after parsing.
  if (length(bag_strings) == 1 && str_length(bag_strings) == 0) {
    return(acc)
  }

  bag_counts <- bag_strings %>%
    str_extract("\\d+") %>%
    as.integer()

  bag_colors <- bag_strings %>%
    str_extract("[^\\d]+") %>%
    unlist() %>%
    trimws()

  s <- sum(
    mapply(
      function(x, y) {
        # Two bags, each containing three bags is 2 + 2 * 3 = 8 bags
        # in total.
        x + x * recurse(y, all_bags, 0)
      },
      bag_counts,
      bag_colors,
      USE.NAMES = TRUE
    )
  )
  acc + s
}

recurse("shiny gold", bags, 0)
```

    ## [1] 126

Very good. We’ll try it on the actual input:

``` r
raw_bags <- parse_bags("input/december07.input")
bags <- separate_bags(raw_bags)
recurse("shiny gold", bags, 0)
```

    ## [1] 38426

Correct :)
