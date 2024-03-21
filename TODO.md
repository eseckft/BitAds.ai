# TODO List

### Ping task
- [x] Make miner ping task async and move it to background instead of main process
  
  Note: not needed
- [x] Make sure that validator ping task have to be in `forward` method

### API client
- [ ] Make BitAds client base class and implement sync (almost) and async version + mocked client
- [x] Instead of `json()` in client use Pydantic models

### Dependency injection
- [x] Make wallet info not global and pass it to necessary classes: APIClient, BaseStorage

### Implementation in variation
- [x] Consider creating JsonStorage or SQLiteStorage implementation instead of FileStorage
  
  Note: not needed

### Global
- [x] Update project to new BitTensor template version
- [ ] Unit tests