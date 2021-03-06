from sys import exit
from typing import Optional, Union

import sys, json
import pyexiv2 as exiv


class _InputFileHandler(object):
	def __init__(self: object, fileName: str):
		assert fileName.endswith('.json')
		self.fileName = fileName
		self.data: dict[str, list[str]]

	def readInputFile(self: object) -> str:
		"""
		Reads a json file and gives the data to the InputFile object, whereafter it returns the root path if it exists\n
		@param self: object
		@return: Optional[str]
		"""
		with open(self.fileName, 'r') as f:
			data = json.loads(f.read())
		self.data = data.copy()
		try:
			[*data].index("path")
			del self.data["path"]
			return data["path"]
		except ValueError:
			return "."

	def getInputInformation(self:object) -> (str, list[str]):
		"""
		Loops over the keys in of the input JSON file, and yields the results to the iterator\n
		@param self: object
		@yield: (str, list[str])
		"""
		for key in self.data.keys():
			yield key, self.data[key]


class TargetFile(object):
	def __init__(self: object, fileName: str, rootPath: Optional[str]):
		self.fileName = fileName
		self.rootPath = rootPath

	def readExistingMetaData(self: object) -> dict[str, list[str]]:
		"""
		Using pyexiv2 to read the metadata from the given file, and returns it for later use\n
		@param self: object\n
		@return: dict[str, list[str]]
		"""
		with exiv.Image(f"{self.rootPath}/{self.fileName}") as f:
			data = f.read_xmp()
		return data

	def writeMetaData(self:object, data: list[str]) -> None:
		"""
		Using pyexiv2 to write the given data as metadata to the file\n
		@param self: object\n
		@return: None
		"""
		with exiv.Image(f"{self.rootPath}/{self.fileName}") as f:
			f.modify_xmp({ "Xmp.dc.subject": data })
		return


def main():
	args = list(map(lambda x: x.lower(), sys.argv))
	try:
		file = args[args.index("-f") +1]
	except RuntimeError:
		exit(
			{
				"Message": "No file provided",
				"ExitCode": 1
			}
		)

	try:
		inputFile = _InputFileHandler(file)
		rootPath = inputFile.readInputFile()
	except AssertionError:
		exit(
				{
					"Message": "The given file did not end with \".js\"",
					"ExitCode": 1
				}
			)

	for file, data in inputFile.getInputInformation():
		try:
			metaFile = TargetFile(file, rootPath)
			metaFile.writeMetaData(data)
		except RuntimeError:
			print(f"{file} does not exist")

if __name__ == '__main__':
	main()
	exit(
			{
				"Message": "Done",
				"ExitCode": 0
			}
		)
