#!/usr/bin/perl -w
#==============================================================================
#
#   CONVERT SIMPLE PLAIN TEXT TO HTML WITH TEX MATH SNIPPETS
#
#   This program takes on standard input a simple text file containing TeX
#   arbitrary math snippets (delimited by '$'s) and produces on standard
#   output an HTML document with PNG images embedded in <IMG> tags.
#
#   This program demonstrates conversion techniques and is not intended for
#   production use.
#
#   Todd S. Lehman
#   February 2012
#

use strict;


#------------------------------------------------------------------------------
#
#   RUN EXTERNAL COMMAND VIA BOURNE SHELL
#

sub run_command (@) {
    my $origcmdline = join(" ", grep {defined} @_);
    return if $origcmdline eq "";

    my $cmdline = $origcmdline;
    $cmdline =~ s/(["\\])/\\$1/g;
    $cmdline = qq{/bin/sh -c "($cmdline) 2>&1"};

    my $output = `$cmdline`;

    my ($exit_value, $signal_num, $dumped_core) = ($?>>8, $?&127, $?&128);
    $exit_value == 0 or die
      "FAILED: $origcmdline\n" .
      "   \$! = $!\n" .
      "   \$@ = $@\n" .
      "   EXIT_VALUE = $exit_value\n" .
      "   SIGNAL_NUM = $signal_num\n" .
      "   DUMPED_CORE = $dumped_core\n" .
      "   OUTPUT = $output\n";

    return $output;
}


#------------------------------------------------------------------------------
#
#   ROUND NUMBER UP TO THE NEXT HIGHER MULTIPLE
#

sub round_up ($$) {
    my ($num, $mod) = @_;
    return $num + ($num % $mod == 0?  0 : ($mod - ($num % $mod)));
}


#------------------------------------------------------------------------------
#
#   FETCH WIDTH AND HEIGHT FROM PNM FILE
#

sub pnm_width_height ($) {
    my ($filename) = @_;
    $filename =~ m/\.pnm$/ or die "$filename: not .pnm";

    open(PNM, '<', $filename) or die "$filename: can't read";
    my $line = <PNM>;  # Skip first line.
    do { $line = <PNM> }
        while $line =~ m/^#/;  # Read next line, skipping comments
    close(PNM);

    my ($width, $height) = ($line =~ m/^(\d+)\s+(\d+)$/);
    defined($width) && defined($height)
        or die "$filename: Couldn't read image size";
    return ($width, $height);
}


#------------------------------------------------------------------------------
#
#  COMPILE LATEX SNIPPET INTO HTML
#
#  This routine caches results in the /tmp directory.  Snippets are named and
#  indexed by their SHA-1 hash.
#

sub tex_to_html ($$) {
    my ($tex_template, $tex_snippet) = @_;

    my $render_antialias_bits = 4;
    my $render_oversample = 4;
    my $display_oversample = 4;
    my $oversample = $render_oversample * $display_oversample;
    my $render_dpi = 96*1.2 * 72.27/72 * $oversample;  # This is 1850.112 dpi.


    # --- Generate SHA-1 hash of TeX input for caching.

    (my $tex_input = $tex_template) =~ s{<SNIPPET>}{$tex_snippet};
    my $hash = do { use Digest::SHA; uc(Digest::SHA::sha1_hex($tex_input)); };
    my $file = "/tmp/tex-$hash";


    # --- If the image has already been compiled, then simply return the
    #     cached result.  Otherwise, continue and create the image.

    if (open(HTML, '<', "$file.html")) {
        my $html = do { local $/; <HTML> };
        close(HTML);
        return $html;
    }


    # --- Write TeX source and compile to PDF.

    open(TEX, '>', "$file.tex") and print TEX $tex_input and close(TEX)
        or die "$file.tex: can't write";

    run_command(
        "pdflatex",
        "-halt-on-error",
        "-output-directory=/tmp",
        "-output-format=pdf",
        "$file.tex",
        ">$file.err 2>&1"
    );


    # --- Convert PDF to PNM using Ghostscript.

    run_command(
        "gs",
        "-q -dNOPAUSE -dBATCH",
        "-dTextAlphaBits=$render_antialias_bits",
        "-dGraphicsAlphaBits=$render_antialias_bits",
        "-r$render_dpi",
        "-sDEVICE=pnmraw",
        "-sOutputFile=$file.pnm",
        "$file.pdf"
    );

    my ($img_width, $img_height) = pnm_width_height("$file.pnm");
    #print "# img_width=$img_width\n";
    #print "# img_height=$img_height\n";
    #print "# \n";


    # --- Read dimensions file written by TeX during processing.
    #
    #     Example of file contents:
    #       snippetdepth = 6.50009pt
    #       snippetheight = 13.53899pt
    #       snippetwidth = 145.4777pt
    #       pagewidth = 153.4777pt
    #       pageheight = 28.03908pt
    #       pagemargin = 4.0pt

    my $dimensions = {};
    do {
        open(DIMENSIONS, '<', "$file.dimensions")
            or die "$file.dimensions: can't read";
        while (<DIMENSIONS>) {
            if (m/^(\S+)\s+=\s+(-?[0-9\.]+)pt$/) {
                my ($value, $length) = ($1, $2);
                $length = $length / 72.27 * $render_dpi;
                $dimensions->{$value} = $length;
            } else {
                die "$file.dimensions: invalid line: $_";
            }
        }
        close(DIMENSIONS);
    };

    #foreach (keys %$dimensions) { print "# $_=$dimensions->{$_}px\n"; }
    #print "# \n";


    # --- Crop bottom, then measure how much was cropped.

    run_command("pnmcrop -white -bottom $file.pnm >$file.bottomcrop.pnm");

    my ($img_width_bottomcrop, $img_height_bottomcrop) =
        pnm_width_height("$file.bottomcrop.pnm");

    my $bottomcrop = $img_height - $img_height_bottomcrop;
    #printf "# Cropping bottom:  %d pixels - %d pixels = %d pixels cropped\n",
    #    $img_height, $img_height_bottomcrop, $bottomcrop;


    # --- Crop top and sides, then measure how much was cropped from the top.

    run_command("pnmcrop -white $file.bottomcrop.pnm >$file.crop.pnm");

    my ($cropped_img_width, $cropped_img_height) =
        pnm_width_height("$file.crop.pnm");

    my $topcrop = $img_height_bottomcrop - $cropped_img_height;
    #printf "# Cropping top:  %d pixels - %d pixels = %d pixels cropped\n",
    #    $img_height_bottomcrop, $cropped_img_height, $topcrop;


    # --- Pad image with specific values on all four sides, in preparation for
    #     downsampling.

    # Calculate bottom padding.
    my $snippet_depth =
        int($dimensions->{snippetdepth} + $dimensions->{pagemargin} + .5)
            - $bottomcrop;
    my $padded_snippet_depth = round_up($snippet_depth, $oversample);
    my $increase_snippet_depth = $padded_snippet_depth - $snippet_depth;
    my $bottom_padding = $increase_snippet_depth;
    #printf "# Padding snippet depth:  %d pixels + %d pixels = %d pixels\n",
    #    $snippet_depth, $increase_snippet_depth, $padded_snippet_depth;


    # --- Next calculate top padding, which depends on bottom padding.

    my $padded_img_height = round_up(
        $cropped_img_height + $bottom_padding,
        $oversample);
    my $top_padding =
        $padded_img_height - ($cropped_img_height + $bottom_padding);
    #printf "# Padding top:  %d pixels + %d pixels = %d pixels\n",
    #    $cropped_img_height, $top_padding, $padded_img_height;


    # --- Calculate left and right side padding.  Distribute padding evenly.

    my $padded_img_width = round_up($cropped_img_width, $oversample);
    my $left_padding = int(($padded_img_width - $cropped_img_width) / 2);
    my $right_padding = ($padded_img_width - $cropped_img_width)
                        - $left_padding;
    #printf "# Padding left = $left_padding pixels\n";
    #printf "# Padding right = $right_padding pixels\n";


    # --- Pad the final image.

    run_command(
        "pnmpad",
        "-white",
        "-bottom=$bottom_padding",
        "-top=$top_padding",
        "-left=$left_padding",
        "-right=$right_padding",
        "$file.crop.pnm",
        ">$file.pad.pnm"
    );


    # --- Sanity check of final size.

    my ($final_pnm_width, $final_pnm_height) =
        pnm_width_height("$file.pad.pnm");
    $final_pnm_width % $oversample == 0
        or die "$final_pnm_width is not a multiple of $oversample";
    $final_pnm_height % $oversample == 0
        or die "$final_pnm_height is not a multiple of $oversample";


    # --- Convert PNM to PNG.

    my $final_png_width  = $final_pnm_width  / $render_oversample;
    my $final_png_height = $final_pnm_height / $render_oversample;

    run_command(
        "cat $file.pad.pnm",
        "| ppmtopgm",
        "| pamscale -reduce $render_oversample",
        "| pnmgamma .3",
        "| pnmtopng -compression=9",
        "> $file.png"
    );


    # --- Convert PNG to HTML.

    my $html_img_width  = $final_png_width  / $display_oversample;
    my $html_img_height = $final_png_height / $display_oversample;

    my $html_img_vertical_align = sprintf("%.0f",
        -$padded_snippet_depth / $oversample);

    (my $html_img_title = $tex_snippet) =~
        s{([&<>'"])}{sprintf("&#%d;",ord($1))}eg;

    my $png_data_base64 = do {
        open(PNG, '<', "$file.png") or die "$file.png: can't open";
        binmode PNG;
        my $png_data = do { local $/; <PNG> };
        close(PNG);
        use MIME::Base64;
        MIME::Base64::encode_base64($png_data);
    };
    #$png_data_base64 =~ s/\s+//g;

    my $html =
        qq{<img\n} .
        qq{ width=$html_img_width} .
        qq{ height=$html_img_height} .
        qq{ style="vertical-align:${html_img_vertical_align}px;"} .
        qq{ title="$html_img_title"} .
        qq{ src="data:image/png;base64,\n$png_data_base64" />};

    open(HTML, '>', "$file.html") and print HTML $html and close(HTML)
        or die "$file.html: can't write";


    # --- Clean up and return result to caller.

    run_command(
        "rm -f",
        "${file}{.*,}.{tex,aux,dvi,err,log,dimensions,pdf,pnm,png}"
    );

    return $html;
}



#------------------------------------------------------------------------------
#
#   MAIN CONTROL
#

binmode(STDIN,  ":utf8");
binmode(STDOUT, ":utf8");
binmode(STDERR, ":utf8");

my $tex_template = do { local $/; <DATA> };
my $input = do { local $/; <STDIN> };

(my $html = $input) =~ s{\$(.*?)\$}{tex_to_html($tex_template,$1)}seg;

$html =~ s{([^\s<>]*<img.*?>[^\s<>]*)}
          {<span style="white-space:nowrap;">$1</span>}sg;

print <<EOT;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html 
 PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title></title>
</head>
<body>
<p>
$html
</p>
</body>
</html>
EOT

exit(0);


#------------------------------------------------------------------------------
#
#   LATEX TEMPLATE
#

__DATA__
\documentclass[10pt]{article}
\pagestyle{empty}
\setlength{\topskip}{0pt}
\setlength{\parindent}{0pt}
\setlength{\abovedisplayskip}{0pt}
\setlength{\belowdisplayskip}{0pt}

\usepackage{geometry}

\usepackage{amsmath}

\newsavebox{\snippetbox}
\newlength{\snippetwidth}
\newlength{\snippetheight}
\newlength{\snippetdepth}
\newlength{\pagewidth}
\newlength{\pageheight}
\newlength{\pagemargin}

\begin{lrbox}{\snippetbox}%
$<SNIPPET>$%
\end{lrbox}

\settowidth{\snippetwidth}{\usebox{\snippetbox}}
\settoheight{\snippetheight}{\usebox{\snippetbox}}
\settodepth{\snippetdepth}{\usebox{\snippetbox}}

\setlength\pagemargin{4pt}

\setlength\pagewidth\snippetwidth
\addtolength\pagewidth\pagemargin
\addtolength\pagewidth\pagemargin

\setlength\pageheight\snippetheight
\addtolength{\pageheight}{\snippetdepth}
\addtolength\pageheight\pagemargin
\addtolength\pageheight\pagemargin

\newwrite\foo
\immediate\openout\foo=\jobname.dimensions
  \immediate\write\foo{snippetdepth = \the\snippetdepth}
  \immediate\write\foo{snippetheight = \the\snippetheight}
  \immediate\write\foo{snippetwidth = \the\snippetwidth}
  \immediate\write\foo{pagewidth = \the\pagewidth}
  \immediate\write\foo{pageheight = \the\pageheight}
  \immediate\write\foo{pagemargin = \the\pagemargin}
\closeout\foo

\geometry{paperwidth=\pagewidth,paperheight=\pageheight,margin=\pagemargin}

\begin{document}%
\usebox{\snippetbox}%
\end{document}
