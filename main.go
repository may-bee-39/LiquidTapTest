package main

import (
  "fmt"
  "io/ioutil"
  "path/filepath"
)

func main() {
  fmt.Println(dirwalk("./logs"))
}

func dirwalk(dir string) []string {
  fmt.Println(dir)
  files, err := ioutil.ReadDir(dir)
  if err != nil {
    panic(err)
  }

  var paths []string
  for _, file := range files {
    if file.IsDir() {
      paths = append(paths, dirwalk(filepath.Join(dir, file.Name()))...)
      continue
    }
    paths = append(paths, filepath.Join(dir, file.Name()))
  }

  return paths
}
