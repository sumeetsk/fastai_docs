
        #################################################
        ### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
        #################################################
        # file to edit: dev_nb/104_new_data_API.ipynb

from fastai import *
from fastai.vision import *

class ItemList():
    "A collection of items with `__len__` and `__getitem__` with `ndarray` indexing semantics"
    def __init__(self, items:Iterator): self.items = np.array(list(items))
    def __len__(self)->int: return len(self.items)
    def __getitem__(self,i:int)->Any: return self.items[i]
    def __repr__(self)->str: return f'{self.__class__.__name__} ({len(self)} items)\n{self.items}'

def join_path(fname:PathOrStr, path:PathOrStr='.')->Path:
    "`Path(path)/Path(fname)`, `path` defaults to current dir"
    return Path(path)/Path(fname)

def join_paths(fnames:FilePathList, path:PathOrStr='.')->Collection[Path]:
    path = Path(path)
    return [join_path(o,path) for o in fnames]

def loadtxt_str(path:PathOrStr)->np.ndarray:
    "Return `ndarray` of `str` of lines of text from `path`"
    return np.loadtxt(str(path), str)

class ImageFileList(ItemList):
    @classmethod
    def from_folder(cls, path:PathOrStr, check_ext:bool=True, recurse=False)->'ImageFileList':
        return cls(get_image_files(path, check_ext=check_ext, recurse=recurse))

    def label_from_func(self, func:Callable)->Collection:
        return LabelList((o,func(o)) for o in self.items)

class LabelList(ItemList):
    @property
    def files(self): return self.items[:,0]

    def split_by_files(self, valid_fnames:FilePathList)->'SplitData':
        valid = [o for o in self.items if o[0] in valid_fnames]
        train = [o for o in self.items if o[0] not in valid_fnames]
        return SplitData(LabelList(train), LabelList(valid))

    def split_by_fname_file(self, fname:PathOrStr, path:PathOrStr='.')->'SplitData':
        fnames = join_paths(loadtxt_str(fname), path)
        return self.split_by_files(fnames)

    def split_by_idx(self, valid_idx:Collection[int])->'SplitData':
        valid = [o for i,o in enumerate(self.items) if i in valid_idx]
        train = [o for i,o in enumerate(self.items) if i not in valid_idx]
        return SplitData(LabelList(train), LabelList(valid))

    def random_split_by_pct(self, valid_pct:float=0.2)->'SplitData':
        rand_idx = np.random.permutation(range(len(self.items)))
        cut = int(valid_pct * len(self.items))
        return self.split_by_idx(rand_idx[:cut])

@dataclass
class SplitData():
    train:LabelList
    valid:LabelList

    @property
    def lists(self): return [self.train,self.valid]

    def datasets(self, dataset_cls:type, tfms:TfmList, **kwargs):
        dss = [dataset_cls(*o.items.T) for o in self.lists]
        return SplitDatasets(*transform_datasets(*dss, tfms=tfms, **kwargs))

@dataclass
class SplitDatasets():
    train_ds:Dataset
    valid_ds:Dataset

    @property
    def datasets(self): return [self.train_ds,self.valid_ds]

    def dataloaders(self, **kwargs):
        return [DataLoader(o, **kwargs) for o in self.datasets]

    def databunch(self, **kwargs): return ImageDataBunch.create(*self.datasets, **kwargs)