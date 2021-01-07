from setuptools import setup
import simplecol

def main():
    setup(
        name="simplecol",
        description="Easy-to-use columnizer for your shell",
        version=simplecol.__version__,
        license=simplecol.__license__,
        author=simplecol.__author__,
        author_email="Seb_Linke@arcor.de",
        url="https://github.com/seblin/simplecol",
        packages=["simplecol"],
        platforms="any",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Topic :: System :: Shells",
        ],
    )

if __name__ == "__main__":
    main()
